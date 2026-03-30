"""
Setu Backend API - The Bridge Agent
Stable Version 1.0.2 - Fixed Task Validation
"""

import os
from datetime import date, datetime
from typing import List, Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
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
school_sessions_db: Dict[str, List[SchoolSession]] = {}

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
    version="1.0.2",
    lifespan=lifespan
)

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
    return {"service": "Setu API", "status": "active", "version": "1.0.2"}

@app.get("/demo/setup")
async def setup_demo_data():
    """Seeds the database with a fully valid Aarav Sharma profile and task"""
    try:
        slug = datetime.now().strftime('%M%S')
        student_id = f"stu_aarav_{slug}"
        
        # 1. Create Student Profile (Matches schemas.py)
        student = StudentProfile(
            id=student_id,
            name="Aarav Sharma",
            grade="Class 11",
            stream="PCM",
            board="CBSE",
            pw_batch_code="YAKEEN_2.0_2026",
            pw_subjects=["Physics", "Chemistry", "Mathematics"]
        )
        
        students_db[student_id] = student
        understanding_db[student_id] = UnderstandingModelEngine(student_id)
        tasks_db[student_id] = []
        school_sessions_db[student_id] = []
        
        # 2. Create Initial Task (FIX: Added missing required fields)
        demo_task = Task(
            id=f"task_{slug}",
            student_id=student_id,
            title="Newton's Laws - Bridge Practice",
            content_type="dpp",
            priority="high",
            concepts_targeted=["Laws of Motion"],
            status="pending",
            # ADDED THESE TO FIX VALIDATION ERRORS:
            created_at=datetime.now(),
            scheduled_date=date.today(),
            estimated_duration_minutes=45
        )
        tasks_db[student_id].append(demo_task)

        return {
            "status": "success",
            "student_id": student_id,
            "message": f"Full profile and task created for {student.name}.",
            "next_step": f"Visit /daily-brief/{student_id}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/daily-brief/{student_id}", response_model=DailyBriefResponse)
async def get_daily_brief(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    engine = TaskAssignmentEngine(student, understanding_db[student_id])
    
    brief = engine.generate_daily_tasks(
        target_date=date.today(),
        pw_schedule=[],
        school_sessions=school_sessions_db.get(student_id, [])
    )
    
    return DailyBriefResponse(brief=brief)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
