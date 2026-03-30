from datetime import datetime
from typing import List, Optional
# Ensure Task is imported from your schemas
from models.schemas import (
    StudentProfile, CaptureInput, Task, SchoolSession
)

# ... (Previous imports and DB initializations remain the same)

@app.get("/demo/setup")  # Changed to GET so you can visit it in a browser tab
async def setup_demo_data():
    """Set up demo data for Aarav Sharma (The Bridge Agent Demo)"""
    try:
        # 1. Create Unique Student ID
        # We use a timestamp so every time you refresh, a 'new' Aarav is created
        timestamp_slug = datetime.now().strftime('%M%S')
        student_id = f"stu_aarav_{timestamp_slug}"
        
        # 2. Initialize Data Structures for this student
        student = StudentProfile(
            id=student_id,
            name="Aarav Sharma",
            grade="Class 11",
            pw_batch_code="YAKEEN_2.0_2026",
            pw_subjects=["Physics", "Chemistry", "Mathematics"]
        )
        
        # Store in your in-memory DBs
        students_db[student_id] = student
        understanding_db[student_id] = UnderstandingModelEngine(student_id)
        tasks_db[student_id] = []
        school_sessions_db[student_id] = []

        # 3. Process Mock School Content
        parser = SchoolContentParser()
        mock_notes = [
            "Newton's Second Law. F=ma derivation. Page 48 numericals.",
            "Rotational Motion: Moment of Inertia. NCERT page 141-145.",
            "Torque: τ = r × F. Page 150 Q1-5 due tomorrow."
        ]
        
        for text in mock_notes:
            capture = CaptureInput(student_id=student_id, quick_text=text)
            result = parser.parse_capture(capture)
            if result.success and result.session:
                school_sessions_db[student_id].append(result.session)

        # 4. Add a specific Task (Ensure Task attributes match your schemas.py)
        # Note: If your Task model requires 'created_at', add it here
        demo_task = Task(
            id=f"task_torque_{timestamp_slug}",
            student_id=student_id,
            title="Torque & Angular Momentum Practice",
            content_type="dpp",
            priority="high",
            concepts_targeted=["Torque", "Rotational Mechanics"],
            status="pending"
        )
        tasks_db[student_id].append(demo_task)

        # 5. Return success JSON
        return {
            "status": "success",
            "message": f"Demo account created for {student.name}",
            "student_id": student_id,
            "next_steps": [
                f"View Brief: /daily-brief/{student_id}",
                f"Check Understanding: /understanding/{student_id}"
            ]
        }

    except Exception as e:
        # This helps you see the error in your browser if the code crashes
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")
