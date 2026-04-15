"""Tests for Pydantic models."""

from __future__ import annotations

from uuid import UUID

from deutero.models import (
    AnalysisPhase,
    CreditBalance,
    InterviewAnalysisStatus,
    ModelTier,
    ParticipationStats,
    Persona,
    PhaseStatus,
    Question,
    StudyGenerateResponse,
    StudyType,
)


class TestEnums:
    def test_study_type_values(self) -> None:
        assert StudyType.USER_EXPERIENCE == "user_experience"
        assert StudyType.SOCIOLOGY == "sociology"
        assert StudyType.CUSTOMER_DEVELOPMENT == "customer_development"
        assert StudyType.POLLING == "polling"

    def test_model_tier_values(self) -> None:
        assert ModelTier.OPEN_WEIGHTS == "open_weights"
        assert ModelTier.PREMIUM == "premium"
        assert ModelTier.FRONTIER == "frontier"

    def test_analysis_phase_values(self) -> None:
        assert AnalysisPhase.INITIAL_ENGAGEMENT == "initial_engagement"
        assert AnalysisPhase.EMERGENT_THEMES == "emergent_themes"


class TestStudyGenerateResponse:
    def test_parse_minimal(self) -> None:
        data = {
            "study_id": "12345678-1234-1234-1234-123456789abc",
        }
        resp = StudyGenerateResponse.model_validate(data)
        assert resp.study_id == UUID("12345678-1234-1234-1234-123456789abc")
        assert resp.study_name == ""
        assert resp.research_questions == []

    def test_parse_full(self) -> None:
        data = {
            "study_id": "12345678-1234-1234-1234-123456789abc",
            "study_name": "UX Study: Onboarding",
            "study_description": "A study about onboarding.",
            "research_questions": [{"id": "1", "question": "How?"}],
            "research_objectives": [{"id": "1", "objective": "Understand pain"}],
            "xml_file": "<xml/>",
            "url": "https://example.com",
        }
        resp = StudyGenerateResponse.model_validate(data)
        assert resp.study_name == "UX Study: Onboarding"
        assert len(resp.research_questions) == 1


class TestParticipationStats:
    def test_parse(self) -> None:
        data = {
            "survey_id": "12345678-1234-1234-1234-123456789abc",
            "total_interviews": 10,
            "completed_interviews": 7,
            "incomplete_interviews": 3,
            "completion_rate": 70.0,
            "max_responses": 20,
            "quota_fill_rate": 35.0,
            "quota_remaining": 13,
        }
        stats = ParticipationStats.model_validate(data)
        assert stats.total_interviews == 10
        assert stats.quota_remaining == 13


class TestQuestion:
    def test_parse(self) -> None:
        data = {
            "id": "abc-123",
            "question": "How satisfied are you?",
            "scale": {"minScale": 1, "maxScale": 5, "minLabel": "Low", "maxLabel": "High"},
        }
        q = Question.model_validate(data)
        assert q.question == "How satisfied are you?"
        assert q.scale["maxScale"] == 5


class TestPersona:
    def test_parse(self) -> None:
        p = Persona.model_validate({"persona": "A busy developer", "persona_id": "p1"})
        assert p.persona_id == "p1"


class TestCreditBalance:
    def test_parse(self) -> None:
        data = {
            "available_credits": 100.0,
            "credits_used": 20.0,
            "credits_reserved": 5.0,
            "base_limit": 80.0,
            "purchased_credits": 20.0,
            "rollover_credits": 5.0,
            "is_trial_active": False,
            "trial_credits_used": 0,
            "net_available": 75.0,
        }
        balance = CreditBalance.model_validate(data)
        assert balance.net_available == 75.0


class TestInterviewAnalysisStatus:
    def test_parse(self) -> None:
        data = {
            "interview_id": "int-1",
            "study_id": "study-1",
            "status": "in_progress",
            "phases_completed": 2,
            "total_phases": 4,
            "phases": [
                {"phase": 1, "completed": True, "completed_at": "2025-01-01T00:00:00", "has_output": True},
                {"phase": 2, "completed": True, "completed_at": "2025-01-01T01:00:00", "has_output": True},
                {"phase": 3, "completed": False, "has_output": False},
                {"phase": 4, "completed": False, "has_output": False},
            ],
        }
        status = InterviewAnalysisStatus.model_validate(data)
        assert status.phases_completed == 2
        assert len(status.phases) == 4
        assert status.phases[0].completed is True
