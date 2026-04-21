"""Pydantic-модели данных (DTO) для слоёв аудио, LLM и обучения."""

from lang_learn.schemas.audio import (
    AudioFormat,
    STTRequest,
    STTResult,
    STTSegment,
    TTSRequest,
    TTSResult,
)
from lang_learn.schemas.common import LanguageCode
from lang_learn.schemas.dialog import (
    CorrectionItem,
    DialogSessionContext,
    DialogTurnResult,
    NextDialogAction,
    StructuredDialogResponse,
    VocabularyItem,
)
from lang_learn.schemas.learning import (
    AttemptFeedback,
    AttemptRecord,
    ExercisePayload,
    LearningProfile,
    LessonContext,
)
from lang_learn.schemas.llm import (
    ChatMessage,
    LLMProviderConfig,
    LLMRequest,
    LLMResult,
)
from lang_learn.schemas.persistence import (
    AttemptRow,
    LearningProfileRow,
    LessonRow,
    PronunciationReportRow,
    ReviewQueueRow,
    ScenarioRow,
    SessionLogRow,
    UserRow,
)
from lang_learn.schemas.pre_a0 import (
    ClusterEntry,
    ExerciseKind,
    LetterEntry,
    MinimalPairEntry,
    PreA0Course,
)
from lang_learn.schemas.speech_quality import (
    PhraseScoreLog,
    PronunciationReport,
    PronunciationScores,
    WordAlignmentIssue,
)
from lang_learn.schemas.travel import (
    ScenarioVariation,
    TravelLexeme,
    TravelPhrase,
    TravelScenario,
    TravelScenarioBundle,
)

__all__ = [
    "AttemptRow",
    "AudioFormat",
    "ClusterEntry",
    "AttemptFeedback",
    "CorrectionItem",
    "AttemptRecord",
    "ChatMessage",
    "DialogSessionContext",
    "DialogTurnResult",
    "ExerciseKind",
    "ExercisePayload",
    "LanguageCode",
    "LearningProfile",
    "LearningProfileRow",
    "LLMProviderConfig",
    "LLMRequest",
    "LLMResult",
    "NextDialogAction",
    "MinimalPairEntry",
    "LetterEntry",
    "LessonContext",
    "LessonRow",
    "PreA0Course",
    "PhraseScoreLog",
    "PronunciationReport",
    "PronunciationReportRow",
    "PronunciationScores",
    "WordAlignmentIssue",
    "ReviewQueueRow",
    "ScenarioRow",
    "ScenarioVariation",
    "SessionLogRow",
    "StructuredDialogResponse",
    "STTRequest",
    "TravelLexeme",
    "TravelPhrase",
    "TravelScenario",
    "TravelScenarioBundle",
    "STTResult",
    "STTSegment",
    "TTSRequest",
    "VocabularyItem",
    "TTSResult",
    "UserRow",
]
