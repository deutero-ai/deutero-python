"""Tests for resource methods — verifies correct URL paths and payloads."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from deutero import Deutero


def _make_client(handler) -> Deutero:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://t.test")
    return Deutero(api_key="k", base_url="https://t.test", http_client=http_client)


STUDY_ID = "00000000-0000-0000-0000-000000000001"


class TestStudies:
    def test_generate_sends_correct_payload(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v1/surveys/generate"
            body = json.loads(request.content)
            assert body["study_type"] == "user_experience"
            assert body["business_context"] == "SaaS"
            return httpx.Response(200, json={
                "study_id": STUDY_ID,
                "study_name": "Test",
            })

        c = _make_client(handler)
        resp = c.studies.generate(
            study_type="user_experience",
            business_context="SaaS",
            research_need="Understand churn",
        )
        assert str(resp.study_id) == STUDY_ID
        c.close()

    def test_get_participation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert f"/api/v1/surveys/{STUDY_ID}/participation" in str(request.url)
            return httpx.Response(200, json={
                "survey_id": STUDY_ID,
                "total_interviews": 5,
                "completed_interviews": 3,
                "incomplete_interviews": 2,
                "completion_rate": 60.0,
            })

        c = _make_client(handler)
        stats = c.studies.get_participation(STUDY_ID)
        assert stats.total_interviews == 5
        c.close()

    def test_set_model_tier(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            body = json.loads(request.content)
            assert body["model_tier"] == "frontier"
            return httpx.Response(200, json={
                "survey_id": STUDY_ID,
                "model_tier": "frontier",
                "model_id": "claude-sonnet-4-6",
                "model_provider": "anthropic",
            })

        c = _make_client(handler)
        info = c.studies.set_model_tier(STUDY_ID, model_tier="frontier")
        assert info.model_tier == "frontier"
        c.close()


class TestQuestions:
    def test_generate(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v1/questions/generate"
            body = json.loads(request.content)
            assert body["number_of_questions"] == 5
            return httpx.Response(200, json={
                "survey_id": STUDY_ID,
                "question_list": [
                    {"question_number": 1, "question_type": "text", "question_content": "Tell me about..."}
                ],
                "edit_questions_url": "https://example.com/edit",
                "interview_url": "https://example.com/interview",
                "xml_file": "<xml/>",
            })

        c = _make_client(handler)
        resp = c.questions.generate(study_id=STUDY_ID, number_of_questions=5)
        assert len(resp.question_list) == 1
        c.close()

    def test_get_question(self) -> None:
        qid = "00000000-0000-0000-0000-000000000099"

        def handler(request: httpx.Request) -> httpx.Response:
            assert f"/api/v1/questions/{qid}" in str(request.url)
            return httpx.Response(200, json={
                "id": qid,
                "question": "How do you feel?",
            })

        c = _make_client(handler)
        q = c.questions.get(qid)
        assert q.question == "How do you feel?"
        c.close()

    def test_update_question(self) -> None:
        qid = "00000000-0000-0000-0000-000000000099"

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            body = json.loads(request.content)
            assert body["question"] == "Updated?"
            assert "explanation" not in body
            return httpx.Response(200, json={
                "id": qid,
                "question": "Updated?",
            })

        c = _make_client(handler)
        q = c.questions.update(qid, question="Updated?")
        assert q.question == "Updated?"
        c.close()


class TestPersonas:
    def test_generate(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["number_of_personas"] == 3
            return httpx.Response(200, json={
                "survey_id": STUDY_ID,
                "personas": [
                    {"persona": "Busy developer", "persona_id": "p1"},
                    {"persona": "Product manager", "persona_id": "p2"},
                    {"persona": "Designer", "persona_id": "p3"},
                ],
            })

        c = _make_client(handler)
        resp = c.personas.generate(study_id=STUDY_ID, number_of_personas=3)
        assert len(resp.personas) == 3
        assert resp.personas[0].persona_id == "p1"
        c.close()


class TestInterviews:
    def test_simulate(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["persona_id"] == "p1"
            return httpx.Response(200, json={
                "survey_id": STUDY_ID,
                "persona_id": "p1",
                "transcript_url": "/interviews/?survey_id=x&interview_id=y",
                "credits_used": 2.5,
                "credits_remaining": 47.5,
            })

        c = _make_client(handler)
        resp = c.interviews.simulate(study_id=STUDY_ID, persona_id="p1")
        assert resp.credits_used == 2.5
        c.close()


class TestAnalysis:
    def test_run_for_study(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert "study_id" in body
            assert body["model_tier"] == "premium"
            return httpx.Response(200, json={
                "success": True,
                "interviews_queued": 2,
                "interviews": [
                    {"interview_id": "i1", "study_id": STUDY_ID},
                    {"interview_id": "i2", "study_id": STUDY_ID},
                ],
                "message": "Queued 2",
            })

        c = _make_client(handler)
        resp = c.analysis.run(study_id=STUDY_ID, model_tier="premium")
        assert resp.interviews_queued == 2
        c.close()

    def test_get_status(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "survey_id" in str(request.url)
            return httpx.Response(200, json={
                "study_id": STUDY_ID,
                "total_interviews": 1,
                "interviews": [{
                    "interview_id": "i1",
                    "study_id": STUDY_ID,
                    "status": "completed",
                    "phases_completed": 4,
                    "total_phases": 4,
                    "phases": [
                        {"phase": i, "completed": True, "has_output": True}
                        for i in range(1, 5)
                    ],
                }],
            })

        c = _make_client(handler)
        resp = c.analysis.get_status(study_id=STUDY_ID)
        assert resp.total_interviews == 1
        assert resp.interviews[0].status == "completed"
        c.close()

    def test_get_interview_results(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "phase=emergent_themes" in str(request.url)
            return httpx.Response(200, json={
                "interview_id": "i1",
                "phase": "emergent_themes",
                "xml_output": "<themes>...</themes>",
                "completed_at": "2025-01-01T00:00:00",
            })

        c = _make_client(handler)
        resp = c.analysis.get_interview_results(interview_id="i1", phase="emergent_themes")
        assert resp.xml_output is not None
        c.close()


class TestCredits:
    def test_get_balance(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/api/v1/credits/balance"
            return httpx.Response(200, json={
                "available_credits": 100.0,
                "credits_used": 20.0,
                "credits_reserved": 5.0,
                "base_limit": 80.0,
                "purchased_credits": 20.0,
                "rollover_credits": 5.0,
                "is_trial_active": False,
                "trial_credits_used": 0,
                "net_available": 75.0,
            })

        c = _make_client(handler)
        balance = c.credits.get_balance()
        assert balance.net_available == 75.0
        c.close()

    def test_estimate_simulation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["num_participants"] == 10
            return httpx.Response(200, json={
                "estimated_credits": 25.0,
                "credits_per_interview": 2.5,
                "credits_for_analysis": 0,
                "model_tier": "open_weights",
                "num_participants": 10,
                "num_questions": 8,
            })

        c = _make_client(handler)
        est = c.credits.estimate_simulation(
            survey_id=STUDY_ID,
            num_participants=10,
        )
        assert est.estimated_credits == 25.0
        c.close()
