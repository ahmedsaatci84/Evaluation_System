from .professor import ProfessorTbl
from .participant import ParticipantTbl
from .location import LocationTbl
from .course import CourseTbl
from .training import TrainTbl, TrainParticipantTbl
from .evaluation import EvaluationTab
from .contact import ContactMessage
from .system import UserProfile, SystemSettings

__all__ = [
    'ProfessorTbl',
    'ParticipantTbl',
    'LocationTbl',
    'CourseTbl',
    'TrainTbl',
    'TrainParticipantTbl',
    'EvaluationTab',
    'ContactMessage',
    'UserProfile',
    'SystemSettings',
]
