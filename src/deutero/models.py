"""Request and response models for the Deutero Study Management API.

Generated from the OpenAPI spec at
https://dashboard.deutero.ai/study-api/api/v1/openapi.json and then kept in sync by hand.
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StudyType(str, enum.Enum):
    """Study methodologies accepted as ``survey_type``."""

    SOCIOLOGY = "sociology"
    USER_EXPERIENCE = "user_experience"
    CUSTOMER_DEVELOPMENT = "customer_development"
    POLLING = "polling"


class ModelTier(str, enum.Enum):
    """Interview model tiers.

    ``"frontier"`` is still accepted by the API as a deprecated alias for ``"premium"``.
    """

    OPEN_WEIGHTS = "open_weights"
    STANDARD = "standard"
    PREMIUM = "premium"


class NodeType(str, enum.Enum):
    """Interview flow step types."""

    START = "start"
    END = "end"
    QUESTION = "question"
    DECISION = "decision"
    EXTRACT = "extract"
    CONTEXT_FETCH = "context_fetch"
    WEBHOOK = "webhook"


class SearchMode(str, enum.Enum):
    """Transcript search modes."""

    STRING = "string"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class AnalysisCategory(str, enum.Enum):
    """Question categories for :meth:`Analysis.list_questions`."""

    TEXT = "text"
    SCALE = "scale"
    OPTIONS = "options"


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectOut(BaseModel):
    """Project."""

    id: UUID
    name: str
    description: Optional[str] = None
    study_count: int = Field(0, description="Number of studies in this project")


class ProjectListOut(BaseModel):
    """Project list."""

    projects: List[ProjectOut]


# ---------------------------------------------------------------------------
# Studies
# ---------------------------------------------------------------------------

class StudyOut(BaseModel):
    """Study."""

    id: UUID
    project_id: Optional[UUID]
    name: str
    description: Optional[str] = None
    survey_type: Optional[str] = None
    research_question: Optional[str] = None
    objectives: Optional[str] = None
    target_population: Optional[str] = None
    methodology: Optional[str] = None
    benefits: Optional[str] = None
    risks: Optional[str] = None
    support_contact: Optional[str] = None
    institution: Optional[str] = None
    language: Optional[str] = None
    anonymous: bool = False
    model_tier: Optional[str] = Field(None, description="Resolved from model_id where possible")
    model_id: Optional[str] = None
    model_provider: Optional[str] = None
    redirect_url: Optional[str] = None
    redirect_url_warning: Optional[str] = Field(
        None,
        description=(
            "Set only on a create/update that changed or questioned the redirect URL you sent — a single-braced "
            "placeholder corrected, or a placeholder we do not substitute. Null on reads"
        ),
    )
    max_responses: Optional[int] = None
    interview_mode: str = "linear"
    status: str = Field(
        "draft",
        description=(
            "Publication status: draft, open, paused or closed. Only an open study admits participants, and an "
            "open study's interview configuration is locked (pause to edit, publish to reopen)"
        ),
    )
    voice_enabled: bool = False
    video_enabled: bool = False
    date_created: Optional[str] = None
    has_welcome: bool = Field(False, description="A welcome/consent message is configured")
    screening_enabled: bool = False
    screening_question_count: int = 0
    characteristics_enabled: bool = False
    characteristics_question_count: int = 0
    question_count: int = Field(0, description="Main interview questions configured")
    dashboard_url: str = Field(..., description="Researcher dashboard page for this study")
    participation_url: str = Field(
        ...,
        description=(
            "Direct text-chat participant link (/chat?survey_id=...) — share this one for text interviews. Append"
            " &source=<campaign tag> and/or &participant_id=<your own id for this person> to record where the "
            "participant came from"
        ),
    )
    short_participation_url: Optional[str] = Field(
        None,
        description="Short text-chat participant link, if a short URL slug is set",
    )
    voice_participation_url: Optional[str] = Field(
        None,
        description="Direct voice-interview participant link, if voice_enabled",
    )
    short_voice_participation_url: Optional[str] = Field(
        None,
        description="Short voice-interview participant link, if voice_enabled and a short URL slug is set",
    )
    video_participation_url: Optional[str] = Field(
        None,
        description="Direct video-interview participant link, if video_enabled",
    )
    short_video_participation_url: Optional[str] = Field(
        None,
        description="Short video-interview participant link, if video_enabled and a short URL slug is set",
    )


class StudySummary(BaseModel):
    """Study summary."""

    id: UUID
    name: str
    description: Optional[str] = None
    survey_type: Optional[str] = None
    language: Optional[str] = None
    date_created: Optional[str] = None
    max_responses: Optional[int] = None
    interview_mode: str = "linear"
    status: str = Field(
        "draft",
        description=(
            "Publication status: draft, open, paused or closed. Only an open study admits participants, and an "
            "open study's interview configuration is locked (pause to edit, publish to reopen)"
        ),
    )


class StudyListOut(BaseModel):
    """Study list."""

    project_id: UUID
    studies: List[StudySummary]


class StudyDraft(BaseModel):
    """AI-drafted study fields, named as :meth:`Studies.create` takes them. Nothing is stored."""

    survey_type: str
    language: str
    name: str = Field(..., description="Generated study name")
    description: Optional[str] = None
    research_question: Optional[str] = Field(None, description="Research questions, separated by blank lines")
    objectives: Optional[str] = Field(None, description="Research objectives, separated by blank lines")
    target_population: Optional[str] = None
    methodology: Optional[str] = None


class StudyDraftFromSiteOut(BaseModel):
    """A study drafted from a product landing page."""

    is_valid: bool = Field(
        ...,
        description=(
            "Whether the page described a product clearly enough to base a study on. When false, draft is null "
            "and rationale says what was missing"
        ),
    )
    rationale: str = Field(..., description="Why this study is worth running, or why no study could be drafted")
    draft: Optional[StudyDraft] = Field(None, description="The suggested user_experience study, when is_valid")
    generations_used: int = Field(
        0,
        description="Drafts generated for this site so far by you, counting this one; limited per site",
    )
    generations_limit: int = Field(..., description="Maximum drafts per site")


# ---------------------------------------------------------------------------
# Welcome & Consent
# ---------------------------------------------------------------------------

class WelcomeOut(BaseModel):
    """Welcome."""

    configured: bool = Field(..., description="Whether a welcome message is set")
    message: str = ""
    consent: bool = False


class WelcomeTranslationOut(BaseModel):
    """Welcome translation."""

    id: UUID
    source_language: str
    target_language: str
    translation_text: str
    timestamp: Optional[str] = None


class WelcomeTranslationListOut(BaseModel):
    """Welcome translation list."""

    translations: List[WelcomeTranslationOut]


class WelcomeDraftOut(BaseModel):
    """AI-drafted welcome/consent text. Not saved — pass ``message`` to :meth:`Welcome.set`."""

    message: str = Field(
        ...,
        description=(
            "Generated welcome/consent text, written to be read aloud by the interviewer, in the study's language"
        ),
    )
    consent_level: str = Field(
        ...,
        description=(
            "How much consent language the study's survey_type called for: full_irb (sociology), standard "
            "(polling), minimal (user_experience, customer_development)"
        ),
    )
    placeholders: List[str] = Field(
        default_factory=list,
        description=(
            "Placeholders like '[Insert researcher name]' left where the study had no value. Fill each in before "
            "saving; participants would otherwise see them verbatim"
        ),
    )


# ---------------------------------------------------------------------------
# Screening
# ---------------------------------------------------------------------------

class ScreeningSettingsOut(BaseModel):
    """Screening settings."""

    enabled: bool
    disqualification_message: str = ""
    redirect_url: str = Field(
        "",
        description="URL disqualified participants are sent to; may contain {{external_participant_id}}",
    )
    redirect_url_warning: Optional[str] = Field(
        None,
        description=(
            "Set only on a write that changed or questioned the redirect URL you sent — a single-braced "
            "placeholder corrected, or a placeholder we do not substitute. Null on reads"
        ),
    )


class ScreeningQuestionOut(BaseModel):
    """Screening question."""

    id: UUID
    question: str
    options: List[str] = []
    acceptable_options: List[str] = []
    question_number: int = 0


class ScreeningOut(BaseModel):
    """Screening."""

    settings: ScreeningSettingsOut
    questions: List[ScreeningQuestionOut]


# ---------------------------------------------------------------------------
# Characteristics
# ---------------------------------------------------------------------------

class CharacteristicsSettingsOut(BaseModel):
    """Characteristics settings."""

    enabled: bool
    anonymous: bool


class CharacteristicQuestionOut(BaseModel):
    """Characteristic question."""

    id: UUID
    question: str
    variable: str
    question_type: Optional[str] = None
    options: List[str] = []
    slot_description: Optional[str] = None
    question_number: int = 0


class CharacteristicsOut(BaseModel):
    """Characteristics."""

    settings: CharacteristicsSettingsOut
    questions: List[CharacteristicQuestionOut]


# ---------------------------------------------------------------------------
# Credits
# ---------------------------------------------------------------------------

class CreditBalanceOut(BaseModel):
    """Credit balance."""

    available_credits: float
    credits_used: float
    credits_reserved: float
    base_limit: float
    purchased_credits: float
    rollover_credits: float
    is_trial_active: bool
    trial_credits_used: float
    net_available: float


# ---------------------------------------------------------------------------
# Interview Questions
# ---------------------------------------------------------------------------

class ScaleConfig(BaseModel):
    """Scale config."""

    minScale: int = Field(1, description="Lowest scale value")
    maxScale: int = Field(10, description="Highest scale value")
    minLabel: str = Field("Least", description="Label for the low end")
    maxLabel: str = Field("Most", description="Label for the high end")


class QuestionImageOut(BaseModel):
    """Question image."""

    id: UUID
    gcs_url: str
    label: Optional[str] = None
    position: int = 0


class QuestionOut(BaseModel):
    """Question."""

    id: UUID
    question_number: int
    question: str
    type: str = Field(..., description="Effective question type (explicit or inferred)")
    explanation: Optional[str] = None
    scale: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    slots: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    min_select: Optional[int] = None
    max_select: Optional[int] = None
    follow_up: Optional[bool] = None
    min_turns: Optional[int] = None
    max_turns: Optional[int] = None
    expected_image: Optional[str] = None
    images: List[QuestionImageOut] = []


class QuestionListOut(BaseModel):
    """Question list."""

    study_id: UUID
    questions: List[QuestionOut]


class GeneratedQuestionsOut(BaseModel):
    """Questions added by AI generation."""

    study_id: UUID
    questions: List[QuestionOut] = Field(..., description="The questions this call added, in interview order")
    skipped_image_questions: int = Field(
        0,
        description=(
            "Image-upload questions the generator proposed but that were not added, because this plan has no "
            "vision-capable interview model"
        ),
    )


class EthicsCheck(BaseModel):
    """Ethics check."""

    passed: bool = Field(..., description="False if any question raises an ethical concern")
    issues: Optional[List[str]] = Field(None, description="Specific concerns; empty when passed")


class LanguageIssues(BaseModel):
    """Language issues."""

    clarity: Optional[str] = Field(None, description="Clarity problem, or null if clear")
    grammar: Optional[str] = Field(None, description="Grammar problem, or null if correct")
    spelling: Optional[str] = Field(None, description="Spelling problem, or null if correct")


class RedundancyCheck(BaseModel):
    """Redundancy check."""

    is_redundant: bool = Field(False, description="Whether this question overlaps another")
    overlaps_with: Optional[List[int]] = Field(None, description="1-based number values of the questions it overlaps")
    description: Optional[str] = Field(None, description="How they overlap, or null")


class QuestionValidation(BaseModel):
    """Question validation."""

    number: int = Field(..., description="1-based position in interview order (question 1 is the first)")
    question_id: Optional[UUID] = Field(None, description="The question this finding refers to")
    has_issues: bool = Field(False, description="Whether anything was flagged")
    language_issues: Optional[LanguageIssues] = None
    redundancy: Optional[RedundancyCheck] = None
    suggestions: Optional[str] = Field(None, description="How to improve the question, or null if it is fine")


class ValidationOut(BaseModel):
    """Validation."""

    study_id: UUID
    ethics_check: EthicsCheck
    questions: List[QuestionValidation] = Field(..., description="One entry per validated question, in interview order")


# ---------------------------------------------------------------------------
# Interview Flow
# ---------------------------------------------------------------------------

class FlowNode(BaseModel):
    """One step in the interview flow."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        description=(
            "Your own identifier for this step, unique within the flow (e.g. 'q_pets'). It is preserved "
            "everywhere — validation errors and later edits refer to it. Cannot look like 'n12'."
        ),
    )
    type: Literal['start', 'end', 'question', 'decision', 'extract', 'context_fetch', 'webhook'] = Field(
        ...,
        description="Step type. Call `describe_graph_nodes` for each type's config fields.",
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "Type-specific configuration. A question needs at least `qtype` and `text`; a decision needs `mode`. "
            "See `describe_graph_nodes`."
        ),
    )
    max_revisits: Optional[int] = Field(
        None,
        description=(
            "Repeat limit. Required on every step inside a loop: the interview takes the default path out once "
            "the step has run this many times."
        ),
    )
    after: Optional[str] = Field(
        None,
        description=(
            "extract and webhook steps only: the id of the question step this runs immediately after. These steps"
            " are never listed in `edges`."
        ),
    )
    before: Optional[str] = Field(
        None,
        description=(
            "context_fetch steps only: the id of the question step that uses the data it brings in. The fetch "
            "runs just before that question."
        ),
    )


class FlowEdge(BaseModel):
    """A connection from one step to the next."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    from_: str = Field(..., alias="from", description="Step id the path leaves from.")
    to: str = Field(..., description="Step id the path leads to.")
    condition: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            'On a path out of a decision step: a single test, {"var": "has_pets", "op": "eq", "value": "Yes"}. '
            "Operators: eq, neq, in, contains, gt, gte, lt, lte, is_set, not_set. Compound logic (all/any/not) is"
            " not accepted — chain two decision steps."
        ),
    )
    class_: Optional[str] = Field(
        None,
        alias="class",
        description="On a path out of an llm_classifier decision: the class label this path handles.",
    )
    default: bool = Field(
        False,
        description=(
            "The 'otherwise' path, taken when no condition matches. A decision step with several paths needs "
            "exactly one — unless its conditions cover every possible answer of a choices or scale question."
        ),
    )
    priority: int = Field(0, description="Evaluation order for paths out of the same decision step; lowest first.")


class FlowDocument(BaseModel):
    """A complete interview flow. `variables`, `entry` and `back_edge` are derived by the compiler — sending them is an
    error rather than a silent no-op.
    """

    model_config = ConfigDict(extra="forbid")

    nodes: List[FlowNode] = Field(..., description="Every step in the flow. Exactly one `start`, at least one `end`.")
    edges: Optional[List[FlowEdge]] = Field(
        None,
        description=(
            "Connections between start/end/question/decision steps only. extract, webhook and context_fetch steps"
            " attach with `after`/`before` instead."
        ),
    )


class PatchOp(BaseModel):
    """One edit applied to the stored flow."""

    model_config = ConfigDict(populate_by_name=True)

    op: Literal['add_node', 'update_node', 'remove_node', 'add_edge', 'update_edge', 'remove_edge'] = Field(
        ...,
        description="Which edit to make.",
    )
    node: Optional[FlowNode] = Field(None, description="add_node: the step to add.")
    edge: Optional[FlowEdge] = Field(None, description="add_edge: the connection to add.")
    id: Optional[str] = Field(None, description="update_node / remove_node: the step id.")
    config: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "update_node: config keys to merge into the step. Keys you omit keep their current value; pass null "
            "to clear one."
        ),
    )
    max_revisits: Optional[int] = Field(None, description="update_node: new repeat limit.")
    after: Optional[str] = Field(None, description="update_node: re-attach an extract/webhook step.")
    before: Optional[str] = Field(None, description="update_node: re-attach a context_fetch step.")
    from_: Optional[str] = Field(
        None,
        alias="from",
        description="update_edge / remove_edge: the connection's source step.",
    )
    to: Optional[str] = Field(None, description="update_edge / remove_edge: the connection's target step.")
    condition: Optional[Dict[str, Any]] = Field(None, description="update_edge: replacement condition.")
    class_: Optional[str] = Field(None, alias="class", description="update_edge: replacement class label.")
    default: Optional[bool] = Field(None, description="update_edge: make this the 'otherwise' path.")
    priority: Optional[int] = Field(None, description="update_edge: new evaluation order.")


class FlowCheckError(BaseModel):
    """One problem found in a flow."""

    node_id: Optional[str] = Field(None, description="The step the problem is on, using your own ids.")
    code: str = Field(..., description="Stable machine-readable code, e.g. 'no_default', 'unreachable'.")
    message: str = Field(..., description="Plain-language explanation of what to fix.")


class GraphOut(BaseModel):
    """A study's interview flow and its current state."""

    study_id: UUID
    interview_mode: str = Field(
        ...,
        description=(
            "'graph' if interviews follow this flow, 'linear' if they follow the plain question list. Change it "
            "with `activate_graph`/`deactivate_graph`."
        ),
    )
    graph_version: int = Field(..., description="Increments on every successful save; 0 if no flow exists.")
    is_active: bool = Field(..., description="Whether this flow is the study's active interview script.")
    has_compiled_ir: bool = Field(
        ...,
        description="Whether the stored flow last compiled cleanly. Required before activating.",
    )
    flow: Optional[FlowDocument] = Field(None, description="The stored flow, or null if none exists yet.")
    errors: Optional[List[FlowCheckError]] = Field(None, description="Problems with the stored flow, if any.")


class GraphCheckOut(BaseModel):
    """Result of checking or saving a flow."""

    valid: bool = Field(..., description="True when the flow has no problems.")
    saved: bool = Field(..., description="Whether the flow was written. Always false for `check_graph`.")
    graph_version: int = Field(..., description="The stored version after this call.")
    errors: Optional[List[FlowCheckError]] = Field(
        None,
        description="Every problem found. Fix these and check again; nothing is saved while any remain.",
    )
    compiled: Optional[Dict[str, Any]] = Field(
        None,
        description=(
            "The compiled flow when valid: the derived `variables` table and the final execution order with "
            "extract/webhook/context_fetch steps spliced in. Use it to confirm attachments landed where you "
            "meant."
        ),
    )


class GraphModeOut(BaseModel):
    """Result of activating or deactivating graph mode."""

    study_id: UUID
    interview_mode: str = Field(..., description="'graph' or 'linear'.")
    is_active: bool


class FlowSignalOut(BaseModel):
    """The delivery config behind one 'Send a signal' (webhook) step."""

    step_id: str = Field(
        ...,
        description=(
            "The step's id as you authored it — the same id set_graph, patch_graph and the interview effects log "
            "use."
        ),
    )
    url: Optional[str] = Field(None, description="Where this step POSTs.")
    method: str = Field("POST", description="HTTP method used for the delivery.")
    signal_type: Optional[str] = Field(
        None,
        description="Event-type label carried in the signed envelope's `type` field.",
    )
    enabled: bool = Field(True, description="False means the interviewer skips this step's delivery.")
    signing_secret: str = Field(
        ...,
        description=(
            "Standard Webhooks signing secret (`whsec_…`) this step's deliveries are signed with. Minted when the"
            " step is first saved and kept stable across later saves, so it can be read back here — verify every "
            "delivery against it before acting on the body."
        ),
    )
    updated_at: Optional[str] = None


class FlowSignalsOut(BaseModel):
    """Flow signals."""

    study_id: UUID
    graph_version: int = Field(0, description="Stored flow version these signals belong to.")
    signals: Optional[List[FlowSignalOut]] = Field(
        None,
        description=(
            "One entry per 'Send a signal' step in the saved flow; empty when the flow has none (or the study has"
            " no flow at all)."
        ),
    )


# ---------------------------------------------------------------------------
# Recruitment
# ---------------------------------------------------------------------------

class RecruitmentOut(BaseModel):
    """Recruitment."""

    study_id: UUID
    participation_url: str = Field(
        ...,
        description=(
            "Direct text-chat participant link (/chat?survey_id=...) — share this one for text interviews. Append"
            " &source=<campaign tag> and/or &participant_id=<your own id for this person> to attribute the "
            "arrival; they are stored as web_source and external_participant_id"
        ),
    )
    short_participation_url: Optional[str] = Field(
        None,
        description="Short text-chat participant link (/chat?s=...); null until a slug is set",
    )
    voice_participation_url: Optional[str] = Field(
        None,
        description=(
            "Direct voice-interview participant link (/voice?survey_id=...), if voice is enabled for this study"
        ),
    )
    short_voice_participation_url: Optional[str] = Field(
        None,
        description="Short voice-interview participant link (/voice?s=...), if voice is enabled and a slug is set",
    )
    video_participation_url: Optional[str] = Field(
        None,
        description=(
            "Direct video-interview participant link (/video?survey_id=...), if video is enabled for this study"
        ),
    )
    short_video_participation_url: Optional[str] = Field(
        None,
        description="Short video-interview participant link (/video?s=...), if video is enabled and a slug is set",
    )
    short_url_slug: Optional[str] = Field(None, description="Current short URL slug")
    max_responses: Optional[int] = Field(None, description="Response quota (null = unlimited)")
    completed_interviews: int = Field(0, description="Completed interviews so far")
    quota_remaining: Optional[int] = Field(None, description="Responses remaining until quota (null if unlimited)")
    redirect_url: Optional[str] = Field(
        None,
        description=(
            "URL participants are sent to after completing. May contain {{external_participant_id}}, replaced "
            "with the id this interview arrived with (empty when it arrived with none)"
        ),
    )
    redirect_url_warning: Optional[str] = Field(
        None,
        description=(
            "Set only on a write that changed or questioned the redirect URL you sent — a single-braced "
            "placeholder corrected, or a placeholder we do not substitute. Null on reads, and null when the URL "
            "was stored exactly as given"
        ),
    )
    screening_enabled: bool = False
    characteristics_enabled: bool = False


# ---------------------------------------------------------------------------
# Embed
# ---------------------------------------------------------------------------

class EmbedKeyListOut(BaseModel):
    """Embed key list."""

    keys: List[Dict[str, Any]]


class EmbedSnippetOut(BaseModel):
    """Embed snippet."""

    study_id: UUID
    widget_src: str = Field(..., description="URL of the embed widget script")
    snippet: str = Field(
        ...,
        description=(
            "Basic install snippet using a publishable key, with an example data-metadata attribute — page-"
            "supplied metadata, which a visitor can edit before the interview starts"
        ),
    )
    signed_snippet: str = Field(
        ...,
        description=(
            "Install snippet for signed-token mode (your server mints a JWS HS256 token with the key's signing "
            "secret). Use this when the interview acts on a metadata value: the token's metadata claim is "
            "recorded as verified and overrides any page-supplied value of the same name"
        ),
    )


# ---------------------------------------------------------------------------
# Personas & Simulation
# ---------------------------------------------------------------------------

class PersonaOut(BaseModel):
    """Persona."""

    id: Optional[UUID] = Field(None, description="Null only for an unsaved preview (generate with save=false)")
    study_id: UUID
    content: str = Field(..., description="The persona description the simulated participant plays")
    preview: str = Field("", description="First 100 characters of the content")
    source: str = Field("manual", description="'manual' = written by a researcher, 'generated' = AI-generated")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class PersonaListOut(BaseModel):
    """Persona list."""

    study_id: UUID
    total: int
    personas: List[PersonaOut]


class PersonaGenerateOut(BaseModel):
    """Persona generate."""

    study_id: UUID
    saved: bool = Field(..., description="Whether the personas were persisted")
    personas: List[PersonaOut]


class SimulationOut(BaseModel):
    """Simulation."""

    id: UUID = Field(..., description="Simulation run id")
    study_id: Optional[UUID] = None
    interview_id: Optional[UUID] = Field(
        None,
        description="The interview this run produced; read its transcript through the monitoring endpoints",
    )
    persona_id: Optional[UUID] = None
    status: str = Field(
        ...,
        description=(
            "'running' while the interview is still being conducted, then 'completed' or 'failed'. A run that is "
            "still unsettled two hours after it started reports 'failed': its worker is gone and its credit "
            "reservation has expired, so it can no longer complete."
        ),
    )
    model_id: Optional[str] = None
    model_provider: Optional[str] = None
    deliver_signals: bool = Field(False, description="Whether this run's signals were sent for real")
    credits_used: Optional[float] = Field(None, description="Charged once the run settles; null while it is running")
    error: Optional[str] = Field(
        None,
        description=(
            "Why the run failed, when it did — the refusal that stopped it, the error that ended it, or a note "
            "that nothing ever settled it. Null for a run that is still going or that completed."
        ),
    )
    started_at: Optional[str] = None


class SimulationStartOut(BaseModel):
    """Simulation start."""

    id: UUID = Field(..., description="Simulation run id")
    study_id: Optional[UUID] = None
    interview_id: Optional[UUID] = Field(
        None,
        description="The interview this run produced; read its transcript through the monitoring endpoints",
    )
    persona_id: Optional[UUID] = None
    status: str = Field(
        ...,
        description=(
            "'running' while the interview is still being conducted, then 'completed' or 'failed'. A run that is "
            "still unsettled two hours after it started reports 'failed': its worker is gone and its credit "
            "reservation has expired, so it can no longer complete."
        ),
    )
    model_id: Optional[str] = None
    model_provider: Optional[str] = None
    deliver_signals: bool = Field(False, description="Whether this run's signals were sent for real")
    credits_used: Optional[float] = Field(None, description="Charged once the run settles; null while it is running")
    error: Optional[str] = Field(
        None,
        description=(
            "Why the run failed, when it did — the refusal that stopped it, the error that ended it, or a note "
            "that nothing ever settled it. Null for a run that is still going or that completed."
        ),
    )
    started_at: Optional[str] = None
    estimated_credits: float = Field(
        ...,
        description="Credits reserved for this run; the reservation is released if the run does not complete",
    )


class SimulationListOut(BaseModel):
    """Simulation list."""

    study_id: UUID
    total: int
    simulations: List[SimulationOut]


# ---------------------------------------------------------------------------
# Response Monitoring
# ---------------------------------------------------------------------------

class StudyStatsOut(BaseModel):
    """Study stats."""

    study_id: UUID
    total_interviews: int = Field(..., description="Interviews started (excluding simulations)")
    completed_interviews: int
    incomplete_interviews: int
    completion_rate: float = Field(..., description="Completed / started, as a percentage")
    max_responses: Optional[int] = None
    quota_fill_rate: Optional[float] = Field(
        None,
        description="Completed / max_responses percentage (null if unlimited)",
    )
    quota_remaining: Optional[int] = None
    simulated_interviews: int = Field(0, description="Simulated (persona) interviews")
    test_interviews: int = Field(0, description="Test runs: a researcher taking the study through a preview link")


class InterviewSummary(BaseModel):
    """Interview summary."""

    id: UUID
    participant_id: Optional[UUID] = None
    participant_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    completed: Optional[bool] = None
    simulated: bool = False
    test_run: bool = Field(
        False,
        description=(
            "A researcher's own test through the dashboard's Try Interview / Preview, not a participant. Never "
            "counts toward max_responses; nothing is owed for it"
        ),
    )
    termination_reason: Optional[str] = None
    web_source: Optional[str] = Field(
        None,
        description="Campaign tag the entry link carried (?source=…); null when the link named none",
    )
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for this participant, from the link's ?participant_id= or the embed metadata bag's "
            "participant_id key. Free text from another system — not the participant_id UUID above, and not an "
            "authenticated identity: anyone holding the link can set it"
        ),
    )
    referrer: Optional[str] = Field(
        None,
        description=(
            "HTTP Referer of the participant's first page load; null when the browser sent none (a typed URL, a "
            "QR code, an https→http hop)"
        ),
    )


class InterviewListOut(BaseModel):
    """Interview list."""

    study_id: UUID
    total: int = Field(..., description="Total interviews matching the filters")
    limit: int
    offset: int
    interviews: List[InterviewSummary]


class QualificationOut(BaseModel):
    """Qualification."""

    question: Optional[str] = None
    answer: Optional[str] = None
    is_qualified: Optional[bool] = None


class CharacteristicValueOut(BaseModel):
    """Characteristic value."""

    variable: Optional[str] = None
    value: Optional[str] = None


class EmbedMetadataItem(BaseModel):
    """Embed metadata item."""

    key: str
    value: Optional[Union[str, bool, int, float]] = Field(
        None,
        description="Scalar metadata value (string, number, boolean, or null)",
    )
    provenance: str = Field(
        "client",
        description="'token' = verified by the customer server, 'client' = page-supplied (untrusted)",
    )


class CapturedVariableOut(BaseModel):
    """One captured answer (Interview Flow variable) an interview ended up holding."""

    name: str = Field(..., description="Variable name, as declared in the flow")
    value: Optional[Any] = Field(
        None,
        description=(
            "The captured value: a string, number, boolean, list or object depending on what the capturing step "
            "produces"
        ),
    )
    value_type: Optional[str] = Field(
        None,
        description="Shape of value: 'string', 'number', 'boolean', 'list[string]' or 'object'",
    )
    source: Optional[str] = Field(
        None,
        description=(
            "Kind of step that captured it: 'question' (a question's structured answer), 'extract' (a 'Capture "
            "from response' step), 'fetch' (a 'Bring in data' response) or 'metadata' (embed-widget metadata)"
        ),
    )
    node_id: Optional[str] = Field(None, description="Flow step that last wrote the value (graph studies)")
    node_visit: int = Field(
        0,
        description=(
            "Which visit to that step wrote it (1 = first). Above 1 means the step ran again in a loop and the "
            "value may be a merged accumulation"
        ),
    )
    question_id: Optional[UUID] = Field(None, description="Question that captured it, for a linear (non-graph) study")
    producer: Optional[str] = Field(
        None,
        description=(
            "Human-readable capturing step: the question's text when a question captured it, otherwise the flow "
            "step id"
        ),
    )
    updated_at: Optional[str] = Field(None, description="When the value was last written")


class InterviewDetailOut(BaseModel):
    """Interview detail."""

    id: UUID
    study_id: Optional[UUID] = None
    participant_id: Optional[UUID] = None
    participant_name: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    completed: Optional[bool] = None
    simulated: bool = False
    test_run: bool = Field(
        False,
        description=(
            "A researcher's own test through the dashboard's Try Interview / Preview, not a participant. Never "
            "counts toward max_responses; nothing is owed for it"
        ),
    )
    termination_reason: Optional[str] = None
    web_source: Optional[str] = Field(
        None,
        description="Campaign tag the entry link carried (?source=…); null when the link named none",
    )
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for this participant, from the link's ?participant_id= or the embed metadata bag's "
            "participant_id key. Free text from another system — not the participant_id UUID above, and not an "
            "authenticated identity: anyone holding the link can set it"
        ),
    )
    referrer: Optional[str] = Field(
        None,
        description=(
            "HTTP Referer of the participant's first page load; null when the browser sent none (a typed URL, a "
            "QR code, an https→http hop)"
        ),
    )
    message_count: int = 0
    qualifications: List[QualificationOut] = []
    characteristics: List[CharacteristicValueOut] = []
    embed_metadata: List[EmbedMetadataItem] = []
    variables: List[CapturedVariableOut] = Field(
        default_factory=list,
        description=(
            "Answers this interview captured into flow variables — the structured values branching, piped text "
            "and downstream steps ran on. Empty for a study that captures nothing, including every linear study"
        ),
    )


class InterviewDetailListOut(BaseModel):
    """Full detail for every interview matching a lookup, newest first."""

    study_id: UUID
    external_participant_id: str = Field(..., description="The id that was looked up")
    total: int = Field(
        ...,
        description=(
            "Interviews this id has. More than one is normal — a person can start again after abandoning, and "
            "each attempt is its own interview; the first row is the newest"
        ),
    )
    interviews: List[InterviewDetailOut] = []


class TranscriptMessage(BaseModel):
    """Transcript message."""

    id: UUID
    type: str
    content: str
    question_number: Optional[int] = None
    node_id: Optional[str] = None
    timestamp: Optional[str] = None


class DecisionOutcomeOut(BaseModel):
    """One decision traversal: which way a Branch went, and why."""

    node_id: str = Field(..., description="Graph step id of the Branch")
    node_visit: int = Field(
        0,
        description="Which visit to that step this was (1 = first), so a looped branch has one entry per pass",
    )
    mode: str = Field(
        "llm_classifier",
        description="'llm_classifier' for a Smart Branch, 'deterministic' for a condition Branch",
    )
    classes: List[str] = Field(
        default_factory=list,
        description="Labels the classifier was offered, in the order given",
    )
    raw_label: Optional[str] = Field(
        None,
        description=(
            "What the classifier emitted. Empty when the call failed or returned a label outside the offered set "
            "— either way the traversal took the default path"
        ),
    )
    matched_class: Optional[str] = Field(
        None,
        description="The label that matched an outgoing path; null when nothing matched and the default was taken",
    )
    chosen_node_id: Optional[str] = Field(None, description="The step this traversal routed to")
    used_default: bool = Field(
        False,
        description=(
            "Whether the 'otherwise' path was taken. True for every traversal whose label matched no path — worth"
            " checking when a branch looks like it fired the wrong way"
        ),
    )
    error: Optional[str] = Field(None, description="Set when the classifier call itself failed")
    decided_at: Optional[str] = None


class TranscriptOut(BaseModel):
    """Transcript."""

    interview_id: UUID
    study_id: Optional[UUID] = None
    participant_id: Optional[UUID] = None
    completed: Optional[bool] = None
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for this participant, from the entry link's ?participant_id= or the embed metadata bag's"
            " participant_id key — the id to join this record back to your own records by. Null when the "
            "interview arrived without one"
        ),
    )
    web_source: Optional[str] = Field(
        None,
        description="Campaign tag the entry link carried (?source=…); null when the link named none",
    )
    test_run: bool = Field(
        False,
        description=(
            "A researcher's own test through the dashboard's Try Interview / Preview, not a participant. Never "
            "counts toward max_responses; nothing is owed for it"
        ),
    )
    messages: List[TranscriptMessage]
    variables: List[CapturedVariableOut] = Field(
        default_factory=list,
        description=(
            "Answers this interview captured into flow variables — the structured values branching, piped text "
            "and downstream steps ran on. Empty for a study that captures nothing, including every linear study"
        ),
    )
    decisions: List[DecisionOutcomeOut] = Field(
        default_factory=list,
        description=(
            "Every Branch this interview passed through, in order, with the label chosen and the step it routed "
            "to. Empty for a linear study or a flow with no branching"
        ),
    )


class NodeFetchOut(BaseModel):
    """One execution of a 'Bring in data' (context_fetch) step."""

    node_id: str = Field(..., description="Graph step id that ran the fetch")
    node_visit: int = Field(
        0,
        description="Which visit to that step this was (1 = first), so a looped step has one entry per pass",
    )
    url: Optional[str] = Field(None, description="URL requested, after piped-text rendering")
    method: Optional[str] = None
    request_body: Optional[Dict[str, Any]] = Field(
        None,
        description="Rendered key/value pairs sent as the JSON body (POST) or query params (GET)",
    )
    status_code: Optional[int] = None
    data: Optional[Any] = Field(
        None,
        description=(
            "Parsed JSON response, in full, on success; null when the fetch errored. A non-JSON body arrives as "
            "{'text': ...}"
        ),
    )
    error: Optional[str] = Field(
        None,
        description="Why the fetch failed (transport error, HTTP >= 400, refused URL); null on success",
    )
    ok: bool = Field(..., description="Whether the fetch succeeded")
    created_at: Optional[str] = None


class SignalDeliveryOut(BaseModel):
    """One delivery attempt of a 'Send a signal' (webhook) step."""

    node_id: str = Field(..., description="Graph step id that sent the signal")
    node_visit: int = Field(0, description="Which visit to that step this was (1 = first)")
    event_type: Optional[str] = Field(None, description="The signal type, i.e. the envelope's 'type' field")
    url: Optional[str] = Field(None, description="Endpoint configured for this step")
    msg_id: Optional[str] = Field(None, description="Value of the webhook-id header the receiver dedupes on")
    request_body: Optional[Dict[str, Any]] = Field(
        None,
        description="Rendered body sent as the envelope's 'data' field",
    )
    status_code: Optional[int] = None
    success: bool = False
    attempt: int = Field(
        1,
        description="Attempts made; a transport failure is retried once, an HTTP error status is not",
    )
    dry_run: bool = Field(
        False,
        description=(
            "True when a simulation built and signed this signal but deliberately did not send it (simulations "
            "dry-run signals unless the run opted into real delivery)"
        ),
    )
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class InterviewEffectsOut(BaseModel):
    """What an interview's graph steps did outside the conversation."""

    interview_id: UUID
    study_id: Optional[UUID] = None
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for this participant, from the entry link's ?participant_id= or the embed metadata bag's"
            " participant_id key — the id to join this record back to your own records by. Null when the "
            "interview arrived without one"
        ),
    )
    web_source: Optional[str] = Field(
        None,
        description="Campaign tag the entry link carried (?source=…); null when the link named none",
    )
    simulated: bool = Field(False, description="Whether this was a simulated (persona) interview")
    test_run: bool = Field(
        False,
        description=(
            "A researcher's own test through the dashboard's Try Interview / Preview, not a participant. Never "
            "counts toward max_responses; nothing is owed for it"
        ),
    )
    fetches: Optional[List[NodeFetchOut]] = Field(None, description="'Bring in data' executions, oldest first")
    signals: Optional[List[SignalDeliveryOut]] = Field(None, description="'Send a signal' deliveries, oldest first")


# ---------------------------------------------------------------------------
# Transcript Search
# ---------------------------------------------------------------------------

class InterviewTranscript(BaseModel):
    """Interview transcript."""

    interview_id: UUID
    participant_id: Optional[UUID] = None
    participant_name: Optional[str] = None
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for this participant, from the entry link's ?participant_id= or the embed metadata bag —"
            " what joins this transcript to your own records. Null when the interview arrived without one"
        ),
    )
    web_source: Optional[str] = Field(None, description="Campaign tag the entry link carried (?source=…)")
    start_time: Optional[str] = None
    completed: Optional[bool] = None
    simulated: bool = False
    test_run: bool = Field(
        False,
        description=(
            "A researcher's own test through the dashboard's Try Interview / Preview, not a participant. Never "
            "counts toward max_responses; nothing is owed for it"
        ),
    )
    messages: List[TranscriptMessage]
    variables: List[CapturedVariableOut] = Field(
        default_factory=list,
        description=(
            "Answers this interview captured into flow variables. Empty for a study that captures nothing, "
            "including every linear study"
        ),
    )


class TranscriptsBulkOut(BaseModel):
    """Transcripts bulk."""

    study_id: UUID
    total_interviews: int = Field(..., description="Interviews matching the filters")
    limit: int
    offset: int
    transcripts: List[InterviewTranscript]


class SearchHit(BaseModel):
    """Search hit."""

    message_id: UUID
    interview_id: Optional[UUID] = None
    participant_id: Optional[UUID] = None
    participant_name: Optional[str] = None
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for the participant whose answer this is, from the entry link or embed metadata; null "
            "when the interview arrived without one"
        ),
    )
    question_id: Optional[UUID] = None
    node_id: Optional[str] = None
    question_number: Optional[int] = None
    content: str
    timestamp: Optional[str] = None
    score: float = Field(
        ...,
        description=(
            "Relevance score. Semantic mode: cosine similarity (0-1). String/hybrid modes: reciprocal-rank-fusion"
            " score across the full-text and trigram (and, in hybrid, vector) rankings."
        ),
    )
    sources: List[str] = Field(..., description="Rankings the hit appeared in: 'fulltext', 'trigram', 'vector'")
    test_run: bool = Field(
        False,
        description="The answer comes from a researcher's own test through the dashboard's Try Interview / Preview",
    )


class SearchOut(BaseModel):
    """Search."""

    study_id: UUID
    query: str
    mode: str = Field(..., description="'string', 'semantic', or 'hybrid'")
    hits: List[SearchHit]


# ---------------------------------------------------------------------------
# Analysis & Clustering
# ---------------------------------------------------------------------------

class AnalyzableQuestion(BaseModel):
    """A question eligible for a given analysis view. id is a questions-table ID for linear studies and a graph step ID
    for graph-mode studies — the step id as you authored it, exactly as get_graph reports it (pass it back as
    question_id).
    """

    id: str
    question: str
    question_number: Optional[int] = None
    qtype: Optional[str] = None
    scale: Optional[Dict[str, Any]] = Field(None, description="Scale config (scale questions)")
    options: Optional[List[str]] = Field(None, description="Options (options questions)")
    response_count: Optional[int] = Field(None, description="Canonical answer rows (options questions)")
    distinct_user_count: Optional[int] = Field(None, description="Distinct respondents (text questions)")


class AnalyzableQuestionsOut(BaseModel):
    """Analyzable questions."""

    study_id: UUID
    category: str = Field(..., description="'text', 'scale', or 'options'")
    questions: List[AnalyzableQuestion]


class ScaleResponsesOut(BaseModel):
    """Scale responses."""

    study_id: UUID
    question_id: str
    counts: Dict[str, int] = Field(..., description="Scale value (as string) → number of responses")


class OptionCount(BaseModel):
    """Option count."""

    option: str
    count: int


class OptionsResponsesOut(BaseModel):
    """Options responses."""

    study_id: UUID
    question_id: str
    counts: List[OptionCount]


class Centroid(BaseModel):
    """Centroid."""

    label: str
    x: float
    y: float


class ClusterPoints(BaseModel):
    """Cluster points."""

    name: str = Field(..., description="Thematic cluster label")
    x: List[float]
    y: List[float]
    text: List[str] = Field(..., description="Message contents in this cluster")
    participant_names: Optional[List[str]] = None
    analysis: Optional[str] = Field(None, description="LLM analysis notes")


class ClusteringOut(BaseModel):
    """Clustering."""

    exists: bool = True
    run_id: Optional[UUID] = None
    question_id: Optional[str] = None
    question_number: Optional[int] = None
    n_clusters: Optional[int] = None
    timestamp: Optional[str] = None
    data_points: List[ClusterPoints] = []
    centroids: List[Centroid] = []
    thinking: Optional[str] = Field(None, description="Model reasoning from labeling")


class OptimalClustersOut(BaseModel):
    """Optimal clusters."""

    optimal_k: int
    k_values: List[int]
    inertias: List[float]


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

class WebhookEventTypeOut(BaseModel):
    """One subscribable event, with what it carries."""

    event_type: str
    description: str = Field(..., description="When this event fires")
    data_fields: List[str] = Field(default_factory=list, description="Keys present in the envelope's data object")


class WebhookEventTypeListOut(BaseModel):
    """Webhook event type list."""

    event_types: List[WebhookEventTypeOut]
    envelope: str = Field(..., description="Shape of every delivery body, whatever the event type")
    signature_headers: List[str] = Field(
        default_factory=list,
        description="Headers carrying the Standard Webhooks signature",
    )


class WebhookOut(BaseModel):
    """Webhook."""

    id: UUID
    label: str
    url: str
    enabled: bool = True
    events: List[str] = Field(default_factory=list, description="Subscribed event types; empty means every event")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WebhookListOut(BaseModel):
    """Webhook list."""

    webhooks: List[WebhookOut]
    total: int = 0
    event_types: List[str] = Field(default_factory=list, description="Every subscribable event type, for convenience")


class WebhookCreatedOut(BaseModel):
    """A newly created endpoint, plus the one and only sight of its secret."""

    webhook: WebhookOut
    signing_secret: str = Field(
        ...,
        description=(
            "Standard Webhooks signing secret (whsec_…). **Shown once and never retrievable** — store it now, or "
            "call rotate_webhook_secret later for a new one. Verify every delivery against it before acting on "
            "the body"
        ),
    )


class WebhookSecretOut(BaseModel):
    """Webhook secret."""

    webhook: WebhookOut
    signing_secret: str = Field(
        ...,
        description=(
            "The new signing secret. The previous one stops verifying immediately, so deploy this before the next"
            " delivery"
        ),
    )


class WebhookDeleteOut(BaseModel):
    """Webhook delete."""

    deleted: bool = True
    webhook_id: UUID


class WebhookDeliveryOut(BaseModel):
    """Webhook delivery."""

    id: UUID
    event_type: str
    msg_id: str = Field(..., description="Value of the webhook-id header the receiver dedupes on")
    status_code: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None
    external_participant_id: Optional[str] = Field(
        None,
        description=(
            "Your own id for the participant this delivery was about, as it was sent in the event payload. "
            "Present on interview.started and interview.completed deliveries whose entry link carried one; null "
            "for every event that names no participant. Use it to reconcile what you were told against what you "
            "acted on — filter this endpoint by external_participant_id to find the deliveries for one person, or"
            " list the failures and read this field to see who was never successfully notified."
        ),
    )
    created_at: Optional[str] = None


class WebhookDeliveryListOut(BaseModel):
    """Webhook delivery list."""

    webhook_id: UUID
    total: int = Field(..., description="Deliveries logged for this endpoint")
    limit: int
    offset: int
    deliveries: List[WebhookDeliveryOut] = Field(default_factory=list, description="Newest first")


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------

class CreditCheckOut(BaseModel):
    """Publish-time credit check."""

    per_interview: Optional[float] = Field(None, description="Worst-case credits for one interview")
    modality: str = Field(..., description="The most expensive modality the study allows")
    remaining_responses: Optional[int] = Field(None, description="Null when the study has no response limit")
    estimated_total: Optional[float] = None
    net_available: Optional[float] = None
    can_auto_top_up: bool
    floor_denial: Optional[str] = Field(None, description="Why even one interview would be refused, or null")
    covers_remaining: Optional[bool] = Field(
        None,
        description="Whether the balance covers every remaining response; null when unlimited",
    )


class IssueLocation(BaseModel):
    """Where a validation issue was found."""

    kind: str = Field(
        ...,
        description="question, welcome, screening, characteristics, snowball_message or study",
    )
    number: Optional[int] = Field(None, description="1-based question number, for questions")
    id: Optional[str] = Field(None, description="The question's id (for a flow: your own step id)")


class IssueOut(BaseModel):
    """One issue found by study validation."""

    severity: str = Field(
        ...,
        description="ethical (must be fixed), blocking (must be fixed) or methodological (may be acknowledged)",
    )
    code: str = Field(
        ...,
        description="Stable identifier, e.g. ethics, no_questions, model_not_on_plan, question_quality",
    )
    message: str
    location: IssueLocation


class ValidationRunOut(BaseModel):
    """Result of validating a study's full configuration."""

    run_id: UUID = Field(
        ...,
        description="Pass as acknowledge_validation_run_id to publish despite methodological issues",
    )
    outcome: str = Field(..., description="passed, methodological_issues, ethical_issues or blocking_issues")
    issues: List[IssueOut]
    config_hash: str = Field(..., description="Hash of the configuration that was validated")
    reused: bool = Field(
        ...,
        description="True when an earlier verdict for this exact configuration was reused (no new model call)",
    )


class LatestValidationOut(BaseModel):
    """The most recent validation run for a study."""

    run_id: UUID
    outcome: str
    issues: List[IssueOut]
    created_at: Optional[str] = None
    current: bool = Field(
        ...,
        description="True when it validated the current configuration and would be reused by publish",
    )


class PublicationStatusOut(BaseModel):
    """A study's publication status."""

    status: str = Field(
        ...,
        description=(
            "draft, open, paused or closed. Only open admits participants; only draft, paused and closed are "
            "editable"
        ),
    )
    status_changed_at: Optional[str] = None
    published_at: Optional[str] = None
    plan_tier: str
    open_limit: Optional[int] = Field(None, description="Studies the plan may have open at once; null is unlimited")
    open_count: int = Field(..., description="Studies open now, including this one if open")
    credit_check: CreditCheckOut
    latest_validation: Optional[LatestValidationOut] = None
    changed_since_publish: bool


class PublishOut(BaseModel):
    """Result of publishing a study."""

    status: str
    validation_run_id: Optional[UUID] = None
    already_open: bool = False


class PauseOut(BaseModel):
    """Result of pausing a study."""

    status: str
    in_flight_count: int = Field(
        ...,
        description="Interviews still running; they finish on the configuration they started with",
    )
    in_flight_source: str = Field(..., description="temporal (exact) or database (approximate)")


# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------

class SuccessResponse(BaseModel):
    """Generic acknowledgement for mutations that return no resource body."""

    success: bool = True
    message: str = Field("", description="Human-readable status message")
