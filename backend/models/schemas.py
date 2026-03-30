"""
Setu System - Pydantic Models
Core data structures for the educational bridge agent
"""

from datetime import datetime, date, time
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class ContentSource(str, Enum):
    """Source of educational content"""
    PW_LECTURE = "pw_lecture"
    PW_DPP = "pw_dpp"
    PW_MODULE = "pw_module"
    PW_TEST = "pw_test"
    SCHOOL_BLACKBOARD = "school_blackboard"
    SCHOOL_WHATSAPP = "school_whatsapp"
    SCHOOL_VOICE = "school_voice"
    SCHOOL_TEXTBOOK = "school_textbook"

class QuestionType(str, Enum):
    """Types of questions in DPPs/tests"""
    SINGLE_CORRECT = "single_correct"
    MULTIPLE_CORRECT = "multiple_correct"
    INTEGER_TYPE = "integer_type"
    MATCH_COLUMNS = "match_columns"
    ASSERTION_REASON = "assertion_reason"
    NUMERICAL = "numerical"
    DERIVATION = "derivation"
    THEORY = "theory"

class ErrorType(str, Enum):
    """Classification of student errors"""
    CONCEPTUAL = "conceptual"
    CALCULATION = "calculation"
    FORMULA = "formula"
    READING = "reading"
    CARELESS = "careless"
    UNIT_CONVERSION = "unit_conversion"
    SIGN_CONVENTION = "sign_convention"

class TaskPriority(str, Enum):
    """Task priority levels"""
    HIGH = "high"      # Must do today
    MEDIUM = "medium"  # Should do today
    LOW = "low"        # If time permits
    DEFERRED = "deferred"  # Hidden from view

class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"

class ConceptMastery(str, Enum):
    """Student's mastery level of a concept"""
    NOT_STARTED = "not_started"
    WEAK = "weak"          # < 50%
    MODERATE = "moderate"  # 50-75%
    STRONG = "strong"      # > 75%
    MASTERED = "mastered"  # > 90%

class StressLevel(str, Enum):
    """Student stress indicators"""
    CALM = "calm"
    NORMAL = "normal"
    ELEVATED = "elevated"
    AT_RISK = "at_risk"
    CRISIS = "crisis"


# ============================================================================
# Content Models
# ============================================================================

class TopicNode(BaseModel):
    """A concept/topic in the unified learning graph"""
    id: str = Field(..., description="Unique topic ID")
    name: str
    subject: str  # Physics, Chemistry, Math, Biology
    chapter: str
    
    # NCERT mapping
    ncert_chapter: Optional[str] = None
    ncert_page_range: Optional[str] = None
    
    # PW mapping
    pw_lecture_id: Optional[str] = None
    pw_lecture_date: Optional[date] = None
    pw_dpp_ids: List[str] = Field(default_factory=list)
    
    # Relationships
    prerequisites: List[str] = Field(default_factory=list)
    next_topics: List[str] = Field(default_factory=list)
    
    # Metadata
    difficulty: Literal["easy", "medium", "hard", "advanced"] = "medium"
    jee_weightage: float = Field(0.0, ge=0, le=1)
    board_weightage: float = Field(0.0, ge=0, le=1)


class Question(BaseModel):
    """Individual question from DPP/Module/Test"""
    id: str
    dpp_id: Optional[str] = None
    module_id: Optional[str] = None
    
    # Content
    text: str
    topic_tags: List[str]
    question_type: QuestionType
    difficulty: Literal["easy", "medium", "hard"]
    
    # Metadata
    time_estimate_minutes: int
    formulas_required: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    similar_to: List[str] = Field(default_factory=list)  # Previous year questions
    
    # Answer (for verification)
    answer: Optional[str] = None
    solution_steps: Optional[List[str]] = None


class DPPContent(BaseModel):
    """Daily Practice Problem set from Physics Wallah"""
    id: str
    batch_code: str  # e.g., "YAKEEN_2.0_2026"
    
    # Schedule
    release_date: date
    lecture_id: str
    lecture_topic: str
    
    # Content
    total_questions: int
    questions: List[Question]
    
    # Difficulty distribution
    easy_count: int
    medium_count: int
    hard_count: int
    
    # Estimated time
    estimated_time_minutes: int
    
    # Topics covered
    concepts_tested: List[str]


class SchoolSession(BaseModel):
    """A school class session"""
    id: str
    date: date
    subject: str
    
    # Content extracted
    topic_detected: str
    sub_topics: List[str] = Field(default_factory=list)
    
    # What teacher taught
    key_points: List[str] = Field(default_factory=list)
    formulas_written: List[str] = Field(default_factory=list)
    diagrams_detected: List[str] = Field(default_factory=list)
    
    # Homework assigned
    homework_text: Optional[str] = None
    homework_questions: Optional[int] = None
    page_reference: Optional[str] = None
    deadline: Optional[date] = None
    
    # NCERT mapping
    ncert_chapter: Optional[str] = None
    ncert_page_range: Optional[str] = None
    
    # Cross-reference with PW
    pw_overlap_topics: List[str] = Field(default_factory=list)
    pw_lecture_date: Optional[date] = None  # When PW covered this


# ============================================================================
# Student Models
# ============================================================================

class StudentProfile(BaseModel):
    """Student profile and preferences"""
    id: str
    name: str
    
    # Academic
    grade: str  # "Class 11"
    stream: str  # "Science"
    board: str  # "CBSE"
    
    # PW details
    pw_batch_code: str
    pw_subjects: List[str]  # ["Physics", "Chemistry", "Math"]
    
    # School details
    school_name: Optional[str] = None
    school_timing: tuple[time, time] = (time(8, 0), time(14, 30))
    
    # Study preferences
    study_hours: tuple[time, time] = (time(16, 0), time(22, 30))
    optimal_session_length_minutes: int = 90
    peak_energy_slot: Optional[tuple[time, time]] = None
    
    # Location (for context)
    location_type: Literal["village", "town", "city"] = "village"
    connectivity_quality: Literal["poor", "fair", "good"] = "poor"


class ConceptMasteryState(BaseModel):
    """Student's mastery state for a specific concept"""
    concept_id: str
    
    # Exposure tracking
    exposure_count: int = 0
    first_seen: Optional[date] = None
    last_tested: Optional[date] = None
    
    # Performance
    correct_application_rate: float = Field(0.0, ge=0, le=1)
    confidence_score: float = Field(0.0, ge=0, le=1)
    
    # Error patterns
    error_count: int = 0
    error_patterns: List[str] = Field(default_factory=list)
    specific_weaknesses: List[str] = Field(default_factory=list)
    
    # Status
    mastery_level: ConceptMastery = ConceptMastery.NOT_STARTED
    next_review_due: Optional[date] = None


class ErrorRecord(BaseModel):
    """Detailed record of a student error"""
    id: str
    timestamp: datetime
    
    # Context
    student_id: str
    concept_id: str
    source_type: ContentSource
    source_id: str  # DPP ID, etc.
    question_number: int
    difficulty: str
    
    # Error details
    error_type: ErrorType
    specific_mistake: str
    root_cause: Optional[str] = None
    
    # Interaction data
    time_spent_minutes: int
    hints_used: int
    final_outcome: Literal["wrong", "partial", "correct_after_hints"]
    
    # Pattern linking
    similar_past_errors: List[str] = Field(default_factory=list)


class StudentState(BaseModel):
    """Complete student understanding model"""
    student_id: str
    updated_at: datetime
    
    # Concept mastery map
    concept_mastery: Dict[str, ConceptMasteryState] = Field(default_factory=dict)
    
    # Learning velocity
    theory_absorption_speed: Literal["slow", "medium", "fast"] = "medium"
    numerical_speed: Literal["slow", "medium", "fast"] = "medium"
    revision_need: Literal["low", "medium", "high"] = "medium"
    
    # Session patterns
    average_homework_duration_minutes: int = 45
    common_error_time: Optional[time] = None  # When fatigue sets in
    
    # Stress indicators
    last_week_completion_rate: float = Field(1.0, ge=0, le=1)
    late_submissions: int = 0
    help_seeking_frequency: Literal["decreasing", "stable", "increasing"] = "stable"
    current_stress_level: StressLevel = StressLevel.NORMAL


# ============================================================================
# Task Models
# ============================================================================

class Task(BaseModel):
    """A task assigned to the student"""
    id: str
    student_id: str
    created_at: datetime
    
    # Content
    title: str
    description: Optional[str] = None
    content_type: Literal["dpp", "module", "school_homework", "revision", "micro_lesson"]
    source_id: Optional[str] = None  # DPP ID, etc.
    
    # Scheduling
    scheduled_date: date
    estimated_duration_minutes: int
    deadline: Optional[date] = None
    
    # Priority & Status
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    
    # Dependencies
    depends_on: Optional[str] = None  # Task ID that must complete first
    unlocks: List[str] = Field(default_factory=list)  # Tasks this unlocks
    
    # Context
    concepts_targeted: List[str] = Field(default_factory=list)
    reason: Optional[str] = None  # Why this task was assigned
    
    # Completion tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_duration_minutes: Optional[int] = None
    score: Optional[float] = None  # For DPPs
    errors_made: List[str] = Field(default_factory=list)


class DailyBrief(BaseModel):
    """Morning briefing for the student"""
    date: date
    student_id: str
    generated_at: datetime
    
    # Context
    energy_level: Literal["low", "medium", "high"]
    focus_subject: Optional[str] = None
    
    # Tasks by bucket
    must_do: List[Task] = Field(default_factory=list)
    queued: List[Task] = Field(default_factory=list)
    done: List[Task] = Field(default_factory=list)
    
    # State summary
    overall_progress: Dict[str, float] = Field(default_factory=dict)  # subject -> %
    weak_areas_today: List[str] = Field(default_factory=list)
    streak_days: int = 0
    
    # Special alerts
    stress_alert: Optional[str] = None
    deadline_warnings: List[str] = Field(default_factory=list)


# ============================================================================
# Capture Models
# ============================================================================

class CaptureInput(BaseModel):
    """Input from student capture (post-school)"""
    student_id: str
    timestamp: datetime
    
    # Input methods
    blackboard_photo: Optional[str] = None  # Base64 or path
    voice_note: Optional[str] = None  # Audio file path
    quick_text: Optional[str] = None
    
    # Explicit homework info
    homework_description: Optional[str] = None
    homework_deadline: Optional[date] = None


class CaptureResult(BaseModel):
    """Result of processing capture input"""
    success: bool
    session: Optional[SchoolSession] = None
    extracted_homework: Optional[Task] = None
    
    # Cross-references found
    pw_matches: List[str] = Field(default_factory=list)
    suggested_dpp_questions: List[str] = Field(default_factory=list)
    
    # Insights
    insight: Optional[str] = None


# ============================================================================
# API Request/Response Models
# ============================================================================

class CreateStudentRequest(BaseModel):
    name: str
    grade: str
    pw_batch_code: str
    pw_subjects: List[str]

class CreateStudentResponse(BaseModel):
    student_id: str
    message: str

class CaptureRequest(BaseModel):
    student_id: str
    input: CaptureInput

class CaptureResponse(BaseModel):
    result: CaptureResult

class DailyBriefRequest(BaseModel):
    student_id: str
    date: Optional[date] = None

class DailyBriefResponse(BaseModel):
    brief: DailyBrief

class TaskCompleteRequest(BaseModel):
    task_id: str
    student_id: str
    score: Optional[float] = None
    errors: List[str] = Field(default_factory=list)
    time_taken_minutes: int

class TaskCompleteResponse(BaseModel):
    success: bool
    updated_state: StudentState
    next_tasks_suggested: List[Task]

class UnderstandingModelResponse(BaseModel):
    student_id: str
    state: StudentState
    insights: List[str] = Field(default_factory=list)
