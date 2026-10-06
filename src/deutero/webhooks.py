"""Verify and parse webhook deliveries from Deutero.

Deutero signs every delivery with the `Standard Webhooks <https://www.standardwebhooks.com>`_
scheme. The same code handles both kinds of delivery:

* **Organization webhooks** (``interview.completed``, ``study.full``, …) — use the endpoint's
  ``signing_secret`` from :meth:`Webhooks.create` or :meth:`Webhooks.rotate_secret`.
* **Interview-flow signals** ("Send a signal" steps) — use the step's ``signing_secret``
  from :meth:`Graph.get_signals`. Their ``type`` is the step's signal type and ``data`` is
  the step's rendered body.

Usage (Flask shown; any framework works — pass the **raw** body bytes, not re-serialized JSON)::

    from deutero import webhooks
    from deutero.webhooks import InterviewCompletedEvent

    @app.post("/deutero")
    def receive():
        try:
            event = webhooks.unwrap(request.get_data(), request.headers, secret=SIGNING_SECRET)
        except webhooks.WebhookVerificationError:
            return "", 400
        if isinstance(event, InterviewCompletedEvent):
            reward(event.data.external_participant_id)
        return "", 204
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any, Dict, Mapping, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from deutero.exceptions import WebhookVerificationError

__all__ = [
    "DEFAULT_TOLERANCE",
    "EVENT_TYPES",
    "AnalysisCompletedData",
    "AnalysisCompletedEvent",
    "CreditsExhaustedData",
    "CreditsExhaustedEvent",
    "InterviewCompletedData",
    "InterviewCompletedEvent",
    "InterviewStartedData",
    "InterviewStartedEvent",
    "SimulationCompletedData",
    "SimulationCompletedEvent",
    "StudyCreatedData",
    "StudyCreatedEvent",
    "StudyFullData",
    "StudyFullEvent",
    "WebhookEvent",
    "WebhookVerificationError",
    "parse_event",
    "sign",
    "unwrap",
    "verify",
]

#: Maximum age (and clock skew), in seconds, of a delivery's ``webhook-timestamp``.
DEFAULT_TOLERANCE = 300

_SECRET_PREFIX = "whsec_"
_SIGNATURE_VERSION = "v1"

PayloadInput = Union[bytes, bytearray, str]


# ---------------------------------------------------------------------------
# Event models
# ---------------------------------------------------------------------------

class _EventData(BaseModel):
    # Payloads may gain keys over time; keep them reachable instead of failing.
    model_config = ConfigDict(extra="allow")


class InterviewStartedData(_EventData):
    """``data`` of an ``interview.started`` event."""

    interview_id: Optional[str] = None
    survey_id: Optional[str] = Field(None, description="The study ID (legacy name)")
    participant_id: Optional[str] = Field(None, description="Deutero's own ID for the participant")
    external_participant_id: Optional[str] = Field(
        None, description="Your ID for the participant, from ?participant_id= or embed metadata. Not authenticated."
    )
    web_source: Optional[str] = Field(None, description="The entry link's ?source= tag. Not authenticated.")


class InterviewCompletedData(InterviewStartedData):
    """``data`` of an ``interview.completed`` event."""

    completed: Optional[bool] = None


class AnalysisCompletedData(_EventData):
    """``data`` of an ``analysis.completed`` event."""

    interview_id: Optional[str] = None
    survey_id: Optional[str] = Field(None, description="The study ID (legacy name)")


class SimulationCompletedData(_EventData):
    """``data`` of a ``simulation.completed`` event."""

    interview_id: Optional[str] = None
    survey_id: Optional[str] = Field(None, description="The study ID (legacy name)")


class StudyCreatedData(_EventData):
    """``data`` of a ``study.created`` event."""

    study_id: Optional[str] = None
    survey_id: Optional[str] = Field(None, description="Same as study_id (legacy name)")
    name: Optional[str] = None
    project_id: Optional[str] = None
    created_via: Optional[str] = Field(None, description="'dashboard', 'import' or 'api' (includes MCP clients)")


class CreditsExhaustedData(_EventData):
    """``data`` of a ``credits.exhausted`` event."""

    organization_id: Optional[str] = None


class StudyFullData(_EventData):
    """``data`` of a ``study.full`` event."""

    survey_id: Optional[str] = Field(None, description="The study ID (legacy name)")
    survey_name: Optional[str] = None


class WebhookEvent(BaseModel):
    """A verified delivery: the ``{type, timestamp, data}`` envelope plus delivery headers.

    Known organization events parse into the typed subclasses below. Anything else —
    including interview-flow signals, whose ``type`` is chosen per step — is returned as a
    plain :class:`WebhookEvent` with ``data`` as a dict.
    """

    model_config = ConfigDict(extra="allow")

    type: str
    timestamp: Optional[datetime] = None
    data: Any = None
    webhook_id: Optional[str] = Field(
        None, description="The webhook-id header: unique per message, use it to deduplicate retries"
    )
    simulated: bool = Field(
        False, description="True when the X-Deutero-Simulated header is set (a signal from a simulated interview)"
    )


class InterviewStartedEvent(WebhookEvent):
    """A participant began an interview."""

    data: InterviewStartedData


class InterviewCompletedEvent(WebhookEvent):
    """A participant finished an interview."""

    data: InterviewCompletedData


class AnalysisCompletedEvent(WebhookEvent):
    """Thematic analysis finished for an interview."""

    data: AnalysisCompletedData


class SimulationCompletedEvent(WebhookEvent):
    """A simulated (persona) interview run finished."""

    data: SimulationCompletedData


class StudyCreatedEvent(WebhookEvent):
    """A study was created."""

    data: StudyCreatedData


class CreditsExhaustedEvent(WebhookEvent):
    """The organization's credit balance reached zero."""

    data: CreditsExhaustedData


class StudyFullEvent(WebhookEvent):
    """A study reached its ``max_responses`` quota."""

    data: StudyFullData


EVENT_TYPES: Dict[str, Type[WebhookEvent]] = {
    "interview.started": InterviewStartedEvent,
    "interview.completed": InterviewCompletedEvent,
    "analysis.completed": AnalysisCompletedEvent,
    "simulation.completed": SimulationCompletedEvent,
    "study.created": StudyCreatedEvent,
    "credits.exhausted": CreditsExhaustedEvent,
    "study.full": StudyFullEvent,
}


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify(
    payload: PayloadInput,
    headers: Mapping[str, str],
    *,
    secret: str,
    tolerance: Optional[int] = DEFAULT_TOLERANCE,
) -> None:
    """Check a delivery's signature and timestamp, raising if either is wrong.

    Args:
        payload: The raw request body, exactly as received.
        headers: The request headers (any case-insensitive or plain mapping).
        secret: The ``whsec_…`` signing secret for the endpoint or signal step.
        tolerance: Maximum age and clock skew of ``webhook-timestamp``, in seconds.
            ``None`` disables the check (e.g. when replaying stored deliveries).

    Raises:
        WebhookVerificationError: Headers are missing, the timestamp is outside the
            tolerance, or no signature matches.
    """
    msg_id, timestamp, signatures = _signature_headers(headers)

    if tolerance is not None:
        try:
            sent_at = int(timestamp)
        except ValueError:
            raise WebhookVerificationError("Invalid webhook-timestamp header") from None
        now = time.time()
        if sent_at < now - tolerance:
            raise WebhookVerificationError("Webhook timestamp is too old")
        if sent_at > now + tolerance:
            raise WebhookVerificationError("Webhook timestamp is in the future")

    expected = _signature(_decode_secret(secret), msg_id, timestamp, _payload_bytes(payload))
    for candidate in signatures.split():
        version, _, value = candidate.partition(",")
        if version != _SIGNATURE_VERSION:
            continue
        try:
            received = base64.b64decode(value, validate=True)
        except binascii.Error:
            continue
        if hmac.compare_digest(expected, received):
            return
    raise WebhookVerificationError("No matching webhook signature found")


def parse_event(payload: PayloadInput, headers: Optional[Mapping[str, str]] = None) -> WebhookEvent:
    """Parse a delivery body into an event **without** verifying it.

    Only use this on payloads you have already verified, or in tests. Prefer :func:`unwrap`.

    Raises:
        WebhookVerificationError: The body is not a JSON event envelope.
    """
    try:
        body = json.loads(_payload_bytes(payload))
    except ValueError:
        raise WebhookVerificationError("Webhook payload is not valid JSON") from None
    if not isinstance(body, dict) or not isinstance(body.get("type"), str):
        raise WebhookVerificationError("Webhook payload has no event type")

    lowered = _lower(headers or {})
    body.pop("webhook_id", None)
    body.pop("simulated", None)
    extras = {
        "webhook_id": lowered.get("webhook-id"),
        "simulated": lowered.get("x-deutero-simulated", "").strip().lower() == "true",
    }
    model = EVENT_TYPES.get(body["type"], WebhookEvent)
    try:
        return model.model_validate({**body, **extras})
    except PydanticValidationError:
        # A known type whose data no longer fits: still hand it over, untyped.
        return WebhookEvent.model_validate({**body, **extras})


def unwrap(
    payload: PayloadInput,
    headers: Mapping[str, str],
    *,
    secret: str,
    tolerance: Optional[int] = DEFAULT_TOLERANCE,
) -> WebhookEvent:
    """Verify a delivery and parse it into an event.

    See :func:`verify` for arguments. Returns a typed event (e.g.
    :class:`InterviewCompletedEvent`) for known organization events, or a plain
    :class:`WebhookEvent` for signals and unrecognized types.

    Raises:
        WebhookVerificationError: The delivery is not authentic or not an event.
    """
    verify(payload, headers, secret=secret, tolerance=tolerance)
    return parse_event(payload, headers)


def sign(
    payload: PayloadInput,
    *,
    secret: str,
    msg_id: str,
    timestamp: Optional[int] = None,
) -> Dict[str, str]:
    """Build the signature headers Deutero would send with ``payload``.

    Useful for testing your receiver locally.

    Args:
        payload: The body to sign.
        secret: The ``whsec_…`` signing secret.
        msg_id: The message ID to send as ``webhook-id``.
        timestamp: Unix time to sign with (defaults to now).
    """
    ts = str(int(time.time()) if timestamp is None else timestamp)
    digest = _signature(_decode_secret(secret), msg_id, ts, _payload_bytes(payload))
    return {
        "webhook-id": msg_id,
        "webhook-timestamp": ts,
        "webhook-signature": f"{_SIGNATURE_VERSION},{base64.b64encode(digest).decode()}",
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _signature(key: bytes, msg_id: str, timestamp: str, payload: bytes) -> bytes:
    signed = msg_id.encode() + b"." + timestamp.encode() + b"." + payload
    return hmac.new(key, signed, hashlib.sha256).digest()


def _decode_secret(secret: str) -> bytes:
    if not secret:
        raise WebhookVerificationError("Webhook secret is empty")
    raw = secret[len(_SECRET_PREFIX):] if secret.startswith(_SECRET_PREFIX) else secret
    try:
        # Tolerate unpadded secrets; b64decode ignores surplus padding.
        return base64.b64decode(raw + "==")
    except binascii.Error:
        raise WebhookVerificationError("Webhook secret is not valid base64") from None


def _signature_headers(headers: Mapping[str, str]) -> "tuple[str, str, str]":
    lowered = _lower(headers)
    msg_id = lowered.get("webhook-id")
    timestamp = lowered.get("webhook-timestamp")
    signatures = lowered.get("webhook-signature")
    if not (msg_id and timestamp and signatures):
        raise WebhookVerificationError("Missing webhook-id, webhook-timestamp or webhook-signature header")
    return msg_id, timestamp, signatures


def _lower(headers: Mapping[str, str]) -> Dict[str, str]:
    return {str(k).lower(): v for k, v in headers.items()}


def _payload_bytes(payload: PayloadInput) -> bytes:
    return payload.encode() if isinstance(payload, str) else bytes(payload)
