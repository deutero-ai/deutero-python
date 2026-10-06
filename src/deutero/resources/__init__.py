"""Resource namespaces for the Deutero API."""

from deutero.resources.analysis import Analysis, AsyncAnalysis
from deutero.resources.characteristics import AsyncCharacteristics, Characteristics
from deutero.resources.credits import AsyncCredits, Credits
from deutero.resources.embed import AsyncEmbed, Embed
from deutero.resources.graph import AsyncGraph, Graph
from deutero.resources.interviews import AsyncInterviews, Interviews
from deutero.resources.personas import AsyncPersonas, Personas
from deutero.resources.projects import AsyncProjects, Projects
from deutero.resources.questions import AsyncQuestions, Questions
from deutero.resources.recruitment import AsyncRecruitment, Recruitment
from deutero.resources.screening import AsyncScreening, Screening
from deutero.resources.simulations import AsyncSimulations, Simulations
from deutero.resources.studies import AsyncStudies, Studies
from deutero.resources.transcripts import AsyncTranscripts, Transcripts
from deutero.resources.webhooks import AsyncWebhooks, Webhooks
from deutero.resources.welcome import AsyncWelcome, Welcome

__all__ = [
    "Analysis",
    "AsyncAnalysis",
    "Characteristics",
    "AsyncCharacteristics",
    "Credits",
    "AsyncCredits",
    "Embed",
    "AsyncEmbed",
    "Graph",
    "AsyncGraph",
    "Interviews",
    "AsyncInterviews",
    "Personas",
    "AsyncPersonas",
    "Projects",
    "AsyncProjects",
    "Questions",
    "AsyncQuestions",
    "Recruitment",
    "AsyncRecruitment",
    "Screening",
    "AsyncScreening",
    "Simulations",
    "AsyncSimulations",
    "Studies",
    "AsyncStudies",
    "Transcripts",
    "AsyncTranscripts",
    "Webhooks",
    "AsyncWebhooks",
    "Welcome",
    "AsyncWelcome",
]
