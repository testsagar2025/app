"""
Setu Backend API
FastAPI server for the educational bridge agent
"""

from datetime import date, datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    StudentProfile, CreateStudentRequest, CreateStudentResponse,
    CaptureInput, CaptureResponse, CaptureResult,
    DailyBrief, DailyBriefRequest, DailyBriefResponse,
    TaskCompleteRequest, TaskCompleteResponse,
    UnderstandingModelResponse, StudentState,
    DPPContent, SchoolSession
)
from core.understanding_model import UnderstandingModelEngine
from core.task_assignment import TaskAssignmentEngine
from core.content_ingestion import (
    PWContentFetcher, SchoolContentParser, CrossCurriculumMapper
)


# ============================================================================
# In-Memory Storage (Replace with database in production)
# ============================================================================

students_db: dict[str, StudentProfile] = {}
understanding_db: dict[str, UnderstandingModelEngine] = {}
tasks_db: dict[str, list] = {}
pw_schedules_db: dict[str, list] = {}
school_sessions_db: dict[str, list] = {}


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Setu Backend Starting...")
    yield
    print("🛑 Setu Backend Shutting down...")

app = FastAPI(
    title="Setu API",
    description="The Bridge Agent for Hybrid Learners - Bridging NCERT and Physics Wallah",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Setu API",
        "version": "1.0.0",
        "status": "running",
        "message": "The Bridge Agent for Hybrid Learners"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "students": len(students_db)
    }


# ============================================================================
# Student Management
# ============================================================================

@app.post("/students", response_model=CreateStudentResponse)
async def create_student(request: CreateStudentRequest):
    """Create a new student profile"""
    
    student_id = f"stu_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.name[:3].lower()}"
    
    student = StudentProfile(
        id=student_id,
        name=request.name,
        grade=request.grade,
        pw_batch_code=request.pw_batch_code,
        pw_subjects=request.pw_subjects
    )
    
    # Store student
    students_db[student_id] = student
    
    # Initialize understanding model
    understanding_db[student_id] = UnderstandingModelEngine(student_id)
    
    # Initialize empty task list
    tasks_db[student_id] = []
    
    # Fetch PW schedule
    fetcher = PWContentFetcher(request.pw_batch_code)
    pw_schedules_db[student_id] = fetcher.fetch_annual_schedule()
    
    # Initialize empty school sessions
    school_sessions_db[student_id] = []
    
    print(f"✅ Created student: {student_id} - {request.name}")
    
    return CreateStudentResponse(
        student_id=student_id,
        message=f"Welcome, {request.name}! Setu is ready to bridge your learning."
    )


@app.get("/students/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str):
    """Get student profile"""
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    return students_db[student_id]


# ============================================================================
# Content Capture (Post-School Input)
# ============================================================================

@app.post("/capture", response_model=CaptureResponse)
async def capture_content(input_data: CaptureInput):
    """
    Process student capture input after school.
    Accepts photo, voice, or text and extracts structured session data.
    """
    
    student_id = input_data.student_id
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Parse the capture
    parser = SchoolContentParser()
    result = parser.parse_capture(input_data)
    
    if result.success and result.session:
        # Store session
        school_sessions_db[student_id].append(result.session)
        
        # If homework extracted, add to tasks
        if result.extracted_homework:
            tasks_db[student_id].append(result.extracted_homework)
        
        print(f"✅ Captured session for {student_id}: {result.session.topic_detected}")
    
    return CaptureResponse(result=result)


# ============================================================================
# Daily Briefing
# ============================================================================

@app.post("/daily-brief", response_model=DailyBriefResponse)
async def get_daily_brief(request: DailyBriefRequest):
    """
    Generate morning briefing with prioritized tasks.
    This is the core "Daily Calm" feature.
    """
    
    student_id = request.student_id
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    understanding = understanding_db[student_id]
    target_date = request.date or date.today()
    
    # Get PW schedule for the period
    fetcher = PWContentFetcher(student.pw_batch_code)
    pw_dpps = [
        fetcher.fetch_dpp(f"DPP_{i:02d}") 
        for i in range(1, 10)  # Mock DPPs
    ]
    
    # Get school sessions
    school_sessions = school_sessions_db.get(student_id, [])
    
    # Generate daily tasks
    task_engine = TaskAssignmentEngine(student, understanding)
    brief = task_engine.generate_daily_tasks(
        target_date=target_date,
        pw_schedule=pw_dpps,
        school_sessions=school_sessions
    )
    
    # Adjust for stress if needed
    brief = task_engine.adjust_for_stress(brief)
    
    print(f"✅ Generated daily brief for {student_id}: {len(brief.must_do)} must-do tasks")
    
    return DailyBriefResponse(brief=brief)


@app.get("/daily-brief/{student_id}", response_model=DailyBriefResponse)
async def get_daily_brief_get(student_id: str, target_date: Optional[date] = None):
    """GET endpoint for daily brief (convenience)"""
    request = DailyBriefRequest(student_id=student_id, date=target_date)
    return await get_daily_brief(request)


# ============================================================================
# Task Management
# ============================================================================

@app.post("/tasks/complete", response_model=TaskCompleteResponse)
async def complete_task(request: TaskCompleteRequest):
    """
    Mark a task as complete and update understanding model.
    Records errors and updates student state.
    """
    
    student_id = request.student_id
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    understanding = understanding_db[student_id]
    
    # Find the task
    task = None
    for t in tasks_db.get(student_id, []):
        if t.id == request.task_id:
            task = t
            break
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update understanding model
    updated_state = understanding.record_task_completion(
        task=task,
        score=request.score,
        errors=request.errors,
        time_taken_minutes=request.time_taken_minutes
    )
    
    # Mark task complete
    task.status = "completed"
    task.completed_at = datetime.now()
    task.actual_duration_minutes = request.time_taken_minutes
    task.score = request.score
    task.errors_made = request.errors
    
    # Generate next task suggestions
    task_engine = TaskAssignmentEngine(students_db[student_id], understanding)
    next_brief = task_engine.generate_daily_tasks(
        target_date=date.today(),
        pw_schedule=[],
        school_sessions=[]
    )
    
    print(f"✅ Task completed: {request.task_id} - Score: {request.score}")
    
    return TaskCompleteResponse(
        success=True,
        updated_state=understanding.export_state(),
        next_tasks_suggested=next_brief.must_do[:2]
    )


# ============================================================================
# Understanding Model
# ============================================================================

@app.get("/understanding/{student_id}", response_model=UnderstandingModelResponse)
async def get_understanding_model(student_id: str):
    """Get student's complete understanding model"""
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    understanding = understanding_db[student_id]
    state = understanding.export_state()
    insights = understanding.generate_learning_insights()
    
    return UnderstandingModelResponse(
        student_id=student_id,
        state=state,
        insights=insights
    )


@app.get("/understanding/{student_id}/weak-areas")
async def get_weak_areas(student_id: str, limit: int = 5):
    """Get student's weak areas for targeted practice"""
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    understanding = understanding_db[student_id]
    weak_areas = understanding.get_weak_areas(limit)
    
    return {
        "weak_areas": [
            {
                "concept": concept_id,
                "mastery": state.mastery_level.value,
                "confidence": state.confidence_score,
                "error_patterns": state.error_patterns
            }
            for concept_id, state in weak_areas
        ]
    }


@app.get("/understanding/{student_id}/predict/{concept_id}")
async def predict_performance(student_id: str, concept_id: str, difficulty: str = "medium"):
    """Predict performance on a concept"""
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    understanding = understanding_db[student_id]
    probability, insight = understanding.predict_performance(concept_id, difficulty)
    
    return {
        "concept_id": concept_id,
        "predicted_success_probability": probability,
        "insight": insight,
        "difficulty": difficulty
    }


# ============================================================================
# Cross-Curriculum Mapping
# ============================================================================

@app.get("/mapping/school-to-pw")
async def map_school_to_pw(topic: str, page: Optional[str] = None):
    """Map a school topic to PW content"""
    
    mapper = CrossCurriculumMapper()
    mapping = mapper.map_school_to_pw(topic, page)
    
    return {
        "school_topic": topic,
        "school_page": page,
        "pw_mapping": mapping
    }


@app.get("/mapping/unified-schedule/{student_id}")
async def get_unified_schedule(student_id: str):
    """Get unified schedule integrating school and PW"""
    
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    mapper = CrossCurriculumMapper()
    
    school_sessions = school_sessions_db.get(student_id, [])
    
    # Get PW schedule
    student = students_db[student_id]
    fetcher = PWContentFetcher(student.pw_batch_code)
    pw_dpps = [fetcher.fetch_dpp(f"DPP_{i:02d}") for i in range(1, 10)]
    
    unified = mapper.generate_unified_schedule(school_sessions, pw_dpps)
    
    return {
        "student_id": student_id,
        "unified_schedule": unified
    }


# ============================================================================
# PW Content
# ============================================================================

@app.get("/pw/schedule/{batch_code}")
async def get_pw_schedule(batch_code: str):
    """Get Physics Wallah annual schedule"""
    
    fetcher = PWContentFetcher(batch_code)
    schedule = fetcher.fetch_annual_schedule()
    
    return {
        "batch_code": batch_code,
        "schedule": schedule
    }


@app.get("/pw/dpp/{dpp_id}")
async def get_dpp(dpp_id: str, batch_code: str = "YAKEEN_2.0_2026"):
    """Get specific DPP content"""
    
    fetcher = PWContentFetcher(batch_code)
    dpp = fetcher.fetch_dpp(dpp_id)
    
    return dpp


# ============================================================================
# Demo Data
# ============================================================================

@app.post("/demo/setup")
async def setup_demo_data():
    """Set up demo data for Aarav"""
    
    # Create Aarav's profile
    create_request = CreateStudentRequest(
        name="Aarav Sharma",
        grade="Class 11",
        pw_batch_code="YAKEEN_2.0_2026",
        pw_subjects=["Physics", "Chemistry", "Mathematics"]
    )
    
    response = await create_student(create_request)
    student_id = response.student_id
    
    # Add some sample school sessions
    parser = SchoolContentParser()
    
    # Simulate past captures
    captures = [
        CaptureInput(
            student_id=student_id,
            timestamp=datetime(2026, 3, 15, 14, 45, 0),
            quick_text="Today sir taught Laws of Motion, specifically Newton's Second Law. F=ma derivation. Page 48 ke 5 numericals diye hai, kal submit karna hai."
        ),
        CaptureInput(
            student_id=student_id,
            timestamp=datetime(2026, 3, 28, 14, 45, 0),
            quick_text="Rotational Motion start hua. Moment of Inertia, Parallel Axis Theorem. NCERT page 141-145. Homework: 3 derivations."
        ),
        CaptureInput(
            student_id=student_id,
            timestamp=datetime(2026, 3, 30, 14, 45, 0),
            quick_text="Torque and Angular Momentum. Important: τ = dL/dt. Page 150 Q1-5 due tomorrow."
        )
    ]
    
    for capture in captures:
        result = parser.parse_capture(capture)
        if result.success and result.session:
            school_sessions_db[student_id].append(result.session)
    
    # Simulate some task completions with errors
    understanding = understanding_db[student_id]
    
    # Record some sample errors
    sample_task = Task(
        id="sample_task_1",
        student_id=student_id,
        created_at=datetime.now(),
        title="DPP 12 Practice",
        content_type="dpp",
        scheduled_date=date.today(),
        estimated_duration_minutes=45,
        priority="high",
        concepts_targeted=["Torque"]
    )
    
    understanding.record_task_completion(
        task=sample_task,
        score=0.7,
        errors=["Sign convention confusion - used clockwise positive"],
        time_taken_minutes=50
    )
    
    return {
        "message": "Demo data set up successfully",
        "student_id": student_id,
        "student_name": "Aarav Sharma",
        "school_sessions": len(school_sessions_db[student_id]),
        "next_step": f"GET /daily-brief/{student_id} to see morning briefing"
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
