"""Deutero Python SDK — bindings for the Deutero research platform API.

Usage::

    from deutero import Deutero

    client = Deutero(api_key="your-api-key")
    study = client.studies.generate(
        study_type="user_experience",
        business_context="Our SaaS platform helps teams collaborate",
        research_need="Understand onboarding friction points",
    )
"""

from deutero.client import AsyncDeutero, Deutero
from deutero.exceptions import (
    APIError,
    AuthenticationError,
    BadGatewayError,
    ConnectionError,
    DeuteroError,
    InsufficientCreditsError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
    ValidationError,
)
from deutero.models import (
    AgentRequirementsResponse,
    AnalysisJobInfo,
    AnalysisPhase,
    AnalysisRunResponse,
    AnalysisStatusResponse,
    CreditBalance,
    CreditEstimate,
    CrossCaseAnalysisResult,
    InterviewAnalysisResult,
    InterviewAnalysisStatus,
    InterviewSimulateResponse,
    ModelTier,
    ModelTierInfo,
    ParticipationStats,
    Persona,
    PersonaGenerateResponse,
    PhaseStatus,
    Question,
    QuestionGenerateResponse,
    QuestionItem,
    RunMetadata,
    StudyGenerateResponse,
    StudyType,
)

__all__ = [
    # Clients
    "Deutero",
    "AsyncDeutero",
    # Exceptions
    "DeuteroError",
    "APIError",
    "AuthenticationError",
    "BadGatewayError",
    "ConnectionError",
    "InsufficientCreditsError",
    "InternalServerError",
    "NotFoundError",
    "RateLimitError",
    "TimeoutError",
    "ValidationError",
    # Enums
    "AnalysisPhase",
    "ModelTier",
    "StudyType",
    # Models
    "AgentRequirementsResponse",
    "AnalysisJobInfo",
    "AnalysisRunResponse",
    "AnalysisStatusResponse",
    "CreditBalance",
    "CreditEstimate",
    "CrossCaseAnalysisResult",
    "InterviewAnalysisResult",
    "InterviewAnalysisStatus",
    "InterviewSimulateResponse",
    "ModelTierInfo",
    "ParticipationStats",
    "Persona",
    "PersonaGenerateResponse",
    "PhaseStatus",
    "Question",
    "QuestionGenerateResponse",
    "QuestionItem",
    "RunMetadata",
    "StudyGenerateResponse",
]

__version__ = "0.1.0"
