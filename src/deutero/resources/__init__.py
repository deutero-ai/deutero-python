"""Resource namespaces for the Deutero API."""

from deutero.resources.analysis import Analysis, AsyncAnalysis
from deutero.resources.credits import Credits, AsyncCredits
from deutero.resources.interviews import Interviews, AsyncInterviews
from deutero.resources.personas import Personas, AsyncPersonas
from deutero.resources.questions import Questions, AsyncQuestions
from deutero.resources.studies import Studies, AsyncStudies

__all__ = [
    "Analysis",
    "AsyncAnalysis",
    "Credits",
    "AsyncCredits",
    "Interviews",
    "AsyncInterviews",
    "Personas",
    "AsyncPersonas",
    "Questions",
    "AsyncQuestions",
    "Studies",
    "AsyncStudies",
]
