"""Tests for webhook payload verification and parsing."""

from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict

import pytest
from standardwebhooks import Webhook

import deutero
from deutero import webhooks
from deutero.webhooks import (
    InterviewCompletedEvent,
    InterviewStartedEvent,
    StudyCreatedEvent,
    StudyFullEvent,
    WebhookEvent,
    WebhookVerificationError,
)

SECRET = "whsec_" + base64.b64encode(b"0123456789abcdefghijklmn").decode()
OTHER_SECRET = "whsec_" + base64.b64encode(b"nmlkjihgfedcba9876543210").decode()


def _deliver(event_type: str, data: Dict[str, Any], secret: str = SECRET) -> "tuple[bytes, Dict[str, str]]":
    """Build a delivery exactly as the dashboard's WebhookService does."""
    now = datetime.now(timezone.utc)
    msg_id = "msg_0123abcd"
    body = json.dumps({"type": event_type, "timestamp": now.isoformat(), "data": data}, default=str)
    headers = {
        "Content-Type": "application/json",
        "webhook-id": msg_id,
        "webhook-timestamp": str(int(now.timestamp())),
        "webhook-signature": Webhook(secret).sign(msg_id, now, body),
    }
    return body.encode(), headers


COMPLETED = {
    "interview_id": "550e8400-e29b-41d4-a716-446655440000",
    "survey_id": "550e8400-e29b-41d4-a716-446655440001",
    "completed": True,
    "participant_id": "550e8400-e29b-41d4-a716-446655440002",
    "external_participant_id": "u_9f2c",
    "web_source": "newsletter",
}


class TestUnwrap:
    def test_interview_completed_from_server_signature(self) -> None:
        body, headers = _deliver("interview.completed", COMPLETED)
        event = webhooks.unwrap(body, headers, secret=SECRET)
        assert isinstance(event, InterviewCompletedEvent)
        assert event.type == "interview.completed"
        assert event.data.external_participant_id == "u_9f2c"
        assert event.data.completed is True
        assert event.webhook_id == "msg_0123abcd"
        assert event.simulated is False
        assert event.timestamp is not None and event.timestamp.tzinfo is not None

    @pytest.mark.parametrize(
        ("event_type", "data", "model"),
        [
            ("interview.started", {k: v for k, v in COMPLETED.items() if k != "completed"}, InterviewStartedEvent),
            ("study.created", {"study_id": "s", "survey_id": "s", "name": "Churn", "project_id": "p",
                               "created_via": "api"}, StudyCreatedEvent),
            ("study.full", {"survey_id": "s", "survey_name": "Churn"}, StudyFullEvent),
        ],
    )
    def test_known_events_are_typed(self, event_type: str, data: Dict[str, Any], model: type) -> None:
        body, headers = _deliver(event_type, data)
        event = webhooks.unwrap(body, headers, secret=SECRET)
        assert type(event) is model

    def test_every_catalogued_event_has_a_model(self) -> None:
        assert set(webhooks.EVENT_TYPES) == {
            "interview.completed", "interview.started", "analysis.completed", "simulation.completed",
            "study.created", "credits.exhausted", "study.full",
        }

    def test_null_participant_ids_are_allowed(self) -> None:
        body, headers = _deliver("interview.completed", {**COMPLETED, "external_participant_id": None,
                                                         "web_source": None})
        event = webhooks.unwrap(body, headers, secret=SECRET)
        assert isinstance(event, InterviewCompletedEvent)
        assert event.data.external_participant_id is None

    def test_flow_signal_is_generic_and_marked_simulated(self) -> None:
        body, headers = _deliver("lead.qualified", {"email": "a@b.test", "score": "9"})
        headers["X-Deutero-Simulated"] = "true"
        event = webhooks.unwrap(body, headers, secret=SECRET)
        assert type(event) is WebhookEvent
        assert event.type == "lead.qualified"
        assert event.data == {"email": "a@b.test", "score": "9"}
        assert event.simulated is True

    def test_new_data_fields_are_kept(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s", "survey_name": "n", "max_responses": 50})
        event = webhooks.unwrap(body, headers, secret=SECRET)
        assert isinstance(event, StudyFullEvent)
        assert event.data.model_extra == {"max_responses": 50}

    def test_headers_are_case_insensitive_and_str_body_works(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        upper = {k.upper(): v for k, v in headers.items()}
        assert webhooks.unwrap(body.decode(), upper, secret=SECRET).type == "study.full"

    def test_exported_from_package(self) -> None:
        assert deutero.webhooks is webhooks
        assert deutero.WebhookVerificationError is WebhookVerificationError
        assert issubclass(WebhookVerificationError, deutero.DeuteroError)


class TestVerificationFailures:
    def test_wrong_secret(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        with pytest.raises(WebhookVerificationError, match="No matching"):
            webhooks.unwrap(body, headers, secret=OTHER_SECRET)

    def test_tampered_body(self) -> None:
        body, headers = _deliver("interview.completed", COMPLETED)
        tampered = body.replace(b"u_9f2c", b"u_evil")
        with pytest.raises(WebhookVerificationError):
            webhooks.unwrap(tampered, headers, secret=SECRET)

    def test_reserialized_body_fails(self) -> None:
        body, headers = _deliver("interview.completed", COMPLETED)
        reserialized = json.dumps(json.loads(body), separators=(",", ":"))
        with pytest.raises(WebhookVerificationError):
            webhooks.verify(reserialized, headers, secret=SECRET)

    @pytest.mark.parametrize("missing", ["webhook-id", "webhook-timestamp", "webhook-signature"])
    def test_missing_header(self, missing: str) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        del headers[missing]
        with pytest.raises(WebhookVerificationError, match="Missing"):
            webhooks.verify(body, headers, secret=SECRET)

    def test_old_timestamp(self) -> None:
        body = b'{"type":"study.full","data":{}}'
        headers = webhooks.sign(body, secret=SECRET, msg_id="m", timestamp=int(time.time()) - 600)
        with pytest.raises(WebhookVerificationError, match="too old"):
            webhooks.verify(body, headers, secret=SECRET)
        webhooks.verify(body, headers, secret=SECRET, tolerance=None)

    def test_future_timestamp(self) -> None:
        body = b'{"type":"study.full","data":{}}'
        headers = webhooks.sign(body, secret=SECRET, msg_id="m", timestamp=int(time.time()) + 600)
        with pytest.raises(WebhookVerificationError, match="future"):
            webhooks.verify(body, headers, secret=SECRET)

    def test_signed_but_not_an_event(self) -> None:
        body = b"[1, 2, 3]"
        with pytest.raises(WebhookVerificationError, match="no event type"):
            webhooks.unwrap(body, webhooks.sign(body, secret=SECRET, msg_id="m"), secret=SECRET)

    def test_empty_secret(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        with pytest.raises(WebhookVerificationError, match="empty"):
            webhooks.verify(body, headers, secret="")


class TestSignatureHeader:
    def test_accepts_any_of_several_signatures(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        headers["webhook-signature"] = "v1,bm90LWl0 v2,ignored " + headers["webhook-signature"]
        webhooks.verify(body, headers, secret=SECRET)

    def test_secret_without_prefix(self) -> None:
        body, headers = _deliver("study.full", {"survey_id": "s"})
        webhooks.verify(body, headers, secret=SECRET[len("whsec_"):])


class TestSign:
    def test_output_verifies_with_reference_library(self) -> None:
        body = '{"type":"interview.completed","data":{}}'
        headers = webhooks.sign(body, secret=SECRET, msg_id="msg_1")
        assert Webhook(SECRET).verify(body, headers) == {"type": "interview.completed", "data": {}}

    def test_round_trip(self) -> None:
        body = json.dumps({"type": "credits.exhausted", "timestamp": "2026-09-26T10:00:00+00:00",
                           "data": {"organization_id": "o"}})
        event = webhooks.unwrap(body, webhooks.sign(body, secret=SECRET, msg_id="m"), secret=SECRET)
        assert isinstance(event, webhooks.CreditsExhaustedEvent)
        assert event.data.organization_id == "o"


class TestParseEvent:
    def test_malformed_known_event_falls_back_to_generic(self) -> None:
        event = webhooks.parse_event(b'{"type": "study.full", "data": "not-an-object"}')
        assert type(event) is WebhookEvent
        assert event.data == "not-an-object"

    def test_invalid_json(self) -> None:
        with pytest.raises(WebhookVerificationError, match="not valid JSON"):
            webhooks.parse_event(b"not json")
