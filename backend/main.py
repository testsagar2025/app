"""
Setu Backend API - The Bridge Agent
Stable Version 1.0.1 - Fixed Pydantic Validation
"""

import os
from datetime import date, datetime
from typing import List, Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Standard Setu Imports
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
# Global In-Memory Databases
# ============================================================================
students_db: Dict[str, StudentProfile] = {}
understanding_db: Dict[str, UnderstandingModelEngine] = {}
tasks_db: Dict[str, List[Task]] = {}
school_sessions_db: Dict[str, List[SchoolSession]] = []

# ============================================================================
# App Configuration
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Setu Backend: System Online")
    yield
    print("🛑 Setu Backend: System Offline")

app = FastAPI(
    title="Setu API",
    description="The Bridge between NCERT and Physics Wallah",
    version="1.0.1",
    lifespan=lifespan
)

# Enable CORS for the Flutter Web Version
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Routes
# ============================================================================

@app.get("/")
async def root():
    return {"service": "Setu API", "status": "active", "version": "1.0.1"}

@app.get("/demo/setup")
async def setup_demo_data():
    """Seeds the database with a valid Aarav Sharma profile"""
    try:
        # Create unique ID based on current time
        slug = datetime.now().strftime('%M%S')
        student_id = f"stu_aarav_{slug}"
        
        # FIX: Added 'stream' and 'board' to satisfy Pydantic validation
        student = StudentProfile(
            id=student_id,
            name="Aarav Sharma",
            grade="Class 11",
            stream="PCM",      # Physics, Chemistry, Maths
            board="CBSE",      # Central Board
            pw_batch_code="YAKEEN_2.0_2026",
            pw_subjects=["Physics", "Chemistry", "Mathematics"]
        )
        
        # Initialize internal tracking
        students_db[student_id] = student
        understanding_db[student_id] = UnderstandingModelEngine(student_id)
        tasks_db[student_id] = []
        
        # Add a mock task to start with
        demo_task = Task(
            id=f"task_{slug}",
            student_id=student_id,
            title="Newton's Laws - DPP 01",
            content_type="dpp",
            priority="high",
            concepts_targeted=["Laws of Motion"],
            status="pending"
        )
        tasks_db[student_id].append(demo_task)

        return {
            "status": "success",
            "student_id": student_id,
            "message": f"Profile created for {student.name}. Board: {student.board}",
            "next_step": f"Visit /daily-brief/{student_id} to see the Bridge logic."
        }
    except Exception as e:
        # Returns a JSON error instead of crashing the server
        return {"status": "error", "message": str(e)}

@app.get("/daily-brief/{student_id}", response_model=DailyBriefResponse)
async def get_daily_brief(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found in memory")
    
    student = students_db[student_id]
    engine = TaskAssignmentEngine(student, understanding_db[student_id])
    
    # Generate tasks (mocking empty school sessions for now)
    brief = engine.generate_daily_tasks(
        target_date=date.today(),
        pw_schedule=[],
        school_sessions=[]
    )
    
    return DailyBriefResponse(brief=brief)

# ============================================================================
# Execution Logic
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
