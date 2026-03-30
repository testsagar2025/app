"""
Setu Backend API - The Bridge Agent
Final Stable Version for Web & Mobile Deployment
"""

from datetime import date, datetime
from typing import List, Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware

# Ensure these match your local backend/models/schemas.py exactly
from models.schemas import (
    StudentProfile, CreateStudentRequest, CreateStudentResponse,
    CaptureInput, CaptureResponse, CaptureResult,
    DailyBrief, DailyBriefRequest, DailyBriefResponse,
    TaskCompleteRequest, TaskCompleteResponse,
    UnderstandingModelResponse, StudentState,
    DPPContent, SchoolSession, Task
)
from core.understanding_model import UnderstandingModelEngine
from core.task_assignment import TaskAssignmentEngine
from core.content_ingestion import (
    PWContentFetcher, SchoolContentParser, CrossCurriculumMapper
)

# ============================================================================
# In-Memory Storage
# ============================================================================
students_db: Dict[str, StudentProfile] = {}
understanding_db: Dict[str, UnderstandingModelEngine] = {}
tasks_db: Dict[str, List[Task]] = {}
pw_schedules_db: Dict[str, List] = {}
school_sessions_db: Dict[str, List[SchoolSession]] = {}

# ============================================================================
# Lifecycle & App Initialization
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Setu Bridge Agent is Online")
    yield
    print("🛑 Setu Bridge Agent is Offline")

app = FastAPI(
    title="Setu API",
    description="NCERT to Physics Wallah Hybrid Learning Bridge",
    version="1.0.0",
    lifespan=lifespan
)

# CRITICAL FOR WEB VERSION: This allows your browser app to talk to Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Health & Root
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Setu API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# Demo Setup (Browser Friendly)
# ============================================================================

@app.get("/demo/setup")
async def setup_demo_data():
    """Create a demo student and seed initial school data"""
    try:
        # Create a unique ID using minutes/seconds
        slug = datetime.now().strftime('%M%S')
        student_id = f"stu_aarav_{slug}"
        
        # 1. Create Profile
        student = StudentProfile(
            id=student_id,
            name="Aarav Sharma",
            grade="Class 11",
            pw_batch_code="YAKEEN_2.0_2026",
            pw_subjects=["Physics", "Chemistry", "Mathematics"]
        )
        
        # 2. Initialize DB entries
        students_db[student_id] = student
        understanding_db[student_id] = UnderstandingModelEngine(student_id)
        tasks_db[student_id] = []
        school_sessions_db[student_id] = []

        # 3. Mock School Captures
        parser = SchoolContentParser()
        notes = ["Newton's Second Law. F=ma.", "Torque: τ = r × F. Page 150."]
        for text in notes:
            res = parser.parse_capture(CaptureInput(student_id=student_id, quick_text=text))
            if res.success and res.session:
                school_sessions_db[student_id].append(res.session)

        # 4. Create an initial Task
        demo_task = Task(
            id=f"task_{slug}",
            student_id=student_id,
            title="Bridge Practice: Rotational Dynamics",
            content_type="dpp",
            priority="high",
            concepts_targeted=["Torque"],
            status="pending"
        )
        tasks_db[student_id].append(demo_task)

        return {
            "status": "success",
            "student_id": student_id,
            "brief_url": f"/daily-brief/{student_id}",
            "message": "Demo data ready for Aarav Sharma."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============================================================================
# Core API Endpoints
# ============================================================================

@app.get("/daily-brief/{student_id}", response_model=DailyBriefResponse)
async def get_daily_brief(student_id: str, date_str: Optional[str] = None):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    
    # Engine Logic
    task_engine = TaskAssignmentEngine(students_db[student_id], understanding_db[student_id])
    brief = task_engine.generate_daily_tasks(
        target_date=target_date,
        pw_schedule=[], # In real app, fetch from pw_schedules_db
        school_sessions=school_sessions_db.get(student_id, [])
    )
    
    return DailyBriefResponse(brief=brief)

@app.post("/capture", response_model=CaptureResponse)
async def capture_content(input_data: CaptureInput):
    if input_data.student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    parser = SchoolContentParser()
    result = parser.parse_capture(input_data)
    
    if result.success and result.session:
        school_sessions_db[input_data.student_id].append(result.session)
        
    return CaptureResponse(result=result)

@app.get("/understanding/{student_id}", response_model=UnderstandingModelResponse)
async def get_understanding(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    engine = understanding_db[student_id]
    return UnderstandingModelResponse(
        student_id=student_id,
        state=engine.export_state(),
        insights=engine.generate_learning_insights()
    )

# ============================================================================
# Runner
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    # Railway sets the PORT env variable; we use 8000 as fallback
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
