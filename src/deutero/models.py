"""Request and response models for the Deutero API."""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StudyType(str, enum.Enum):
    """Supported study types."""

    USER_EXPERIENCE = "user_experience"
    SOCIOLOGY = "sociology"
    CUSTOMER_DEVELOPMENT = "customer_development"
    POLLING = "polling"


class ModelTier(str, enum.Enum):
    """Available model tiers."""

    OPEN_WEIGHTS = "open_weights"
    PREMIUM = "premium"
    FRONTIER = "frontier"


class AnalysisPhase(str, enum.Enum):
    """Thematic analysis phases for result retrieval."""

    INITIAL_ENGAGEMENT = "initial_engagement"
    INITIAL_NOTING = "initial_noting"
    EMERGENT_THEMES = "emergent_themes"
    CONNECTIONS = "connections"


# ---------------------------------------------------------------------------
# Study / Survey Models
# ---------------------------------------------------------------------------

class StudyGenerateParams(BaseModel):
    """Parameters for generating a new research study."""

    study_type: str = Field(
        "user_experience",
        description="Type of study: 'sociology', 'user_experience', 'customer_development', or 'polling'.",
    )
    language: Optional[str] = Field("English", description="Language for the study.")

    # UX Research fields
    business_context: Optional[str] = Field(None, description="Business or product context (for user_experience).")
    research_need: Optional[str] = Field(None, description="Why the research is being conducted (for user_experience).")
    target_users: Optional[str] = Field(None, description="Primary audience under study (for user_experience).")
    constraints: Optional[str] = Field(None, description="Key constraints or considerations (for user_experience).")

    # Sociology fields
    research_question: Optional[str] = Field(None, description="The research question (for sociology/polling).")
    population_of_interest: Optional[str] = Field(None, description="Population of interest (for sociology).")
    context_or_setting: Optional[str] = Field(None, description="Context or setting (for sociology).")
    key_concepts: Optional[str] = Field(None, description="Key concepts (for sociology).")
    scope_and_boundaries: Optional[str] = Field(None, description="Scope and boundaries (for sociology).")

    # Customer Development fields
    problem_hypothesis: Optional[str] = Field(None, description="Problem hypothesis (for customer_development).")
    customer_segment: Optional[str] = Field(None, description="Customer segment (for customer_development).")
    solution_concept: Optional[str] = Field(None, description="Solution concept (for customer_development).")
    key_assumptions: Optional[str] = Field(None, description="Key assumptions (for customer_development).")
    success_criteria: Optional[str] = Field(None, description="Success criteria (for customer_development).")

    # Polling fields
    population_segment: Optional[str] = Field(None, description="Population segment (for polling).")
    geographic_scope: Optional[str] = Field(None, description="Geographic scope (for polling).")
    survey_context: Optional[str] = Field(None, description="Survey context (for polling).")
    data_quality_requirements: Optional[str] = Field(None, description="Data quality requirements (for polling).")

    model_tier: Optional[str] = Field(None, description="Model tier: 'open_weights', 'premium', or 'frontier'.")


class StudyGenerateResponse(BaseModel):
    """Response from generating a new study."""

    study_id: UUID
    study_name: str = ""
    study_description: str = ""
    research_questions: List[Dict[str, str]] = []
    research_objectives: List[Dict[str, str]] = []
    xml_file: str = ""
    url: str = ""
    agent_instructions: str = ""


class ParticipationStats(BaseModel):
    """Survey participation statistics."""

    survey_id: UUID
    total_interviews: int
    completed_interviews: int
    incomplete_interviews: int
    max_responses: Optional[int] = None
    completion_rate: float
    quota_fill_rate: Optional[float] = None
    quota_remaining: Optional[int] = None


class AgentRequirementsResponse(BaseModel):
    """Agent requirements document response."""

    study_id: UUID
    markdown: str
    filename: str


class ModelTierInfo(BaseModel):
    """Model tier configuration for a survey."""

    survey_id: str
    model_tier: str
    model_id: str
    model_provider: str


# ---------------------------------------------------------------------------
# Question Models
# ---------------------------------------------------------------------------

class QuestionGenerateParams(BaseModel):
    """Parameters for generating questions."""

    survey_id: UUID
    number_of_questions: int = Field(..., gt=0, le=25)
    additional_instructions: Optional[str] = None


class QuestionItem(BaseModel):
    """A single generated question."""

    question_number: int
    question_type: str
    question_content: str
    question_scale: Optional[str] = None
    question_options: Optional[str] = None
    question_slots: Optional[str] = None
    question_images: Optional[str] = None
    question_follow_up: Optional[bool] = None
    question_expected_image: Optional[bool] = None


class QuestionGenerateResponse(BaseModel):
    """Response from question generation."""

    survey_id: UUID
    question_list: List[QuestionItem]
    edit_questions_url: str
    interview_url: str
    xml_file: str
    agent_instructions: str = ""


class Question(BaseModel):
    """A question with its full properties."""

    id: str
    question: str
    explanation: Optional[str] = None
    scale: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    slots: Optional[List[str]] = None
    follow_up: Optional[bool] = None
    min_turns: Optional[int] = None
    max_turns: Optional[int] = None
    expected_image: Optional[str] = None


class QuestionUpdateParams(BaseModel):
    """Parameters for updating a question."""

    question: Optional[str] = Field(None, description="Question text")
    explanation: Optional[str] = Field(None, description="Interviewer guidance/explanation")
    scale: Optional[Dict[str, Any]] = Field(None, description="Scale configuration")
    options: Optional[List[str]] = Field(None, description="Fixed choice options")
    slots: Optional[List[str]] = Field(None, description="Slot names")
    follow_up: Optional[bool] = Field(None, description="Whether follow-up is enabled")
    min_turns: Optional[int] = Field(None, description="Minimum conversation turns")
    max_turns: Optional[int] = Field(None, description="Maximum conversation turns")
    expected_image: Optional[str] = Field(None, description="Expected image description")


# ---------------------------------------------------------------------------
# Persona Models
# ---------------------------------------------------------------------------

class PersonaGenerateParams(BaseModel):
    """Parameters for generating personas."""

    survey_id: UUID
    number_of_personas: int = Field(..., gt=0, le=25)
    additional_instructions: Optional[str] = None


class Persona(BaseModel):
    """A generated persona."""

    persona: str
    persona_id: str


class PersonaGenerateResponse(BaseModel):
    """Response from persona generation."""

    survey_id: UUID
    personas: List[Persona]


# ---------------------------------------------------------------------------
# Interview Models
# ---------------------------------------------------------------------------

class InterviewSimulateParams(BaseModel):
    """Parameters for simulating an interview."""

    survey_id: UUID
    persona_id: str


class InterviewSimulateResponse(BaseModel):
    """Response from interview simulation."""

    survey_id: UUID
    persona_id: str
    transcript_url: str
    credits_used: Optional[float] = None
    credits_remaining: Optional[float] = None


# ---------------------------------------------------------------------------
# Analysis Models
# ---------------------------------------------------------------------------

class AnalysisRunParams(BaseModel):
    """Parameters for running thematic analysis."""

    interview_id: Optional[UUID] = Field(None, description="ID of a specific interview to analyze")
    study_id: Optional[UUID] = Field(None, description="ID of study to analyze all completed interviews")
    model_tier: str = Field("open_weights", description="Model tier: 'open_weights', 'premium', or 'frontier'")
    cross_case_analysis: bool = Field(False, description="Run cross-case analysis for a study")


class AnalysisJobInfo(BaseModel):
    """Info about a queued analysis job."""

    interview_id: str
    study_id: str


class AnalysisRunResponse(BaseModel):
    """Response from running analysis."""

    success: bool
    interviews_queued: int = 0
    interviews: List[AnalysisJobInfo] = []
    message: str
    cross_case_xml: Optional[str] = None
    credits_used: Optional[float] = None
    credits_remaining: Optional[float] = None


class PhaseStatus(BaseModel):
    """Status of a single analysis phase."""

    phase: int
    completed: bool
    completed_at: Optional[str] = None
    has_output: bool


class RunMetadata(BaseModel):
    """Metadata for an analysis run."""

    run_id: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class InterviewAnalysisStatus(BaseModel):
    """Analysis status for a single interview."""

    interview_id: str
    study_id: str
    analysis_id: Optional[str] = None
    status: str
    phases_completed: int
    total_phases: int = 4
    phases: List[PhaseStatus]
    runs: List[RunMetadata] = []
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AnalysisStatusResponse(BaseModel):
    """Response from analysis status query."""

    interview_id: Optional[str] = None
    study_id: Optional[str] = None
    total_interviews: int
    interviews: List[InterviewAnalysisStatus]


class InterviewAnalysisResult(BaseModel):
    """Result of a specific analysis phase for an interview."""

    interview_id: str
    phase: str
    xml_output: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class CrossCaseAnalysisResult(BaseModel):
    """Cross-case analysis result for a survey."""

    survey_id: str
    xml_output: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Credit Models
# ---------------------------------------------------------------------------

class CreditEstimateParams(BaseModel):
    """Parameters for credit estimation."""

    survey_id: UUID
    model_tier: str = Field("open_weights", description="Model tier: 'open_weights', 'premium', or 'frontier'")
    num_participants: int = Field(1, gt=0, description="Number of participants")
    include_analysis: bool = Field(False, description="Whether to include analysis credits")


class CreditEstimate(BaseModel):
    """Credit estimation response."""

    estimated_credits: float
    credits_per_interview: float = 0
    credits_for_analysis: float = 0
    model_tier: str
    num_participants: int
    num_questions: int


class CreditBalance(BaseModel):
    """Current credit balance information."""

    available_credits: float
    credits_used: float
    credits_reserved: float
    base_limit: float
    purchased_credits: float
    rollover_credits: float
    is_trial_active: bool
    trial_credits_used: float = 0
    net_available: float
