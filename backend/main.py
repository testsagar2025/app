# Add this to your imports if not there
from models.schemas import Task 

# ... (rest of your code)

@app.post("/demo/setup")
async def setup_demo_data():
    """Set up demo data for Aarav Sharma"""
    
    # 1. Create Profile
    student_id = f"stu_demo_aarav_{datetime.now().strftime('%M%S')}"
    student = StudentProfile(
        id=student_id,
        name="Aarav Sharma",
        grade="Class 11",
        pw_batch_code="YAKEEN_2.0_2026",
        pw_subjects=["Physics", "Chemistry", "Mathematics"]
    )
    students_db[student_id] = student
    understanding_db[student_id] = UnderstandingModelEngine(student_id)
    tasks_db[student_id] = []
    school_sessions_db[student_id] = []

    # 2. Add Mock School Sessions
    parser = SchoolContentParser()
    mock_texts = [
        "Newton's Second Law. F=ma derivation. Page 48 numericals due tomorrow.",
        "Rotational Motion: Moment of Inertia. NCERT page 141-145.",
        "Torque and Angular Momentum. τ = dL/dt. Page 150 Q1-5."
    ]
    
    for text in mock_texts:
        capture = CaptureInput(student_id=student_id, quick_text=text)
        result = parser.parse_capture(capture)
        if result.success and result.session:
            school_sessions_db[student_id].append(result.session)

    # 3. Add a specific Task to the DB so it can be completed
    demo_task = Task(
        id="task_torque_001",
        student_id=student_id,
        title="Torque Numerical Practice",
        content_type="dpp",
        priority="high",
        concepts_targeted=["Torque"],
        status="pending"
    )
    tasks_db[student_id].append(demo_task)

    return {
        "status": "success",
        "student_id": student_id,
        "instructions": "Now call /daily-brief/" + student_id + " to see the logic in action."
    }
