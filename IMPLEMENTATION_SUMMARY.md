# Setu Implementation Summary

## What is Setu?

**Setu** (सेतु) means "bridge" in Hindi. It's an AI-powered educational assistant designed for students like **Aarav** - high achievers in rural India who are juggling:

- **Traditional CBSE School**: Chalkboard, NCERT textbooks, manual notes
- **Online Competitive Prep**: Physics Wallah lectures, DPPs, module questions

## The Problem

Students live in **two disconnected learning systems**:

```
┌─────────────────────┐     ┌─────────────────────┐
│      SCHOOL         │     │    PHYSICS WALAH    │
├─────────────────────┤     ├─────────────────────┤
│ • Chalkboard        │     │ • Digital lectures  │
│ • NCERT textbooks   │     │ • DPPs (Daily       │
│ • Manual notes      │     │   Practice Problems)│
│ • Weekly tests      │     │ • Module questions  │
│ • Page 48 Q5-10     │     │ • Mock tests        │
└─────────────────────┘     └─────────────────────┘
         ↓                           ↓
    ┌─────────────────────────────────────┐
    │   COGNITIVE LOAD OF TRANSLATION     │
    │   "Which DPP questions match my     │
    │    school homework?"                │
    │   "PW covered this 3 weeks ago -    │
    │    should I revise first?"          │
    │   "School deadline tomorrow,        │
    │    PW test next week - priority?"   │
    └─────────────────────────────────────┘
```

## The Solution

Setu **automatically bridges** these two worlds:

### 1. Content Ingestion

```
┌─────────────────────────────────────────────────────────┐
│              POST-SCHOOL CAPTURE (2:45 PM)              │
├─────────────────────────────────────────────────────────┤
│  📸 Photo of blackboard → OCR → Extract topics          │
│  🎤 Voice note → Transcription → Parse homework         │
│  📝 Quick text → NLP → Structure data                   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              CROSS-CURRICULUM MAPPING                   │
├─────────────────────────────────────────────────────────┤
│  School Topic: "Rotational Motion" (NCERT Ch 7)         │
│  PW Match: "Rotational Dynamics" (Lecture PHY_11_08)    │
│  Insight: "PW covered this 3 weeks ago.                 │
│           DPP 08 Q1-5 are perfect warm-up."             │
└─────────────────────────────────────────────────────────┘
```

### 2. Student Understanding Model

```
┌─────────────────────────────────────────────────────────┐
│           WHAT AARAV KNOWS (Dynamic Graph)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Angular Velocity        ████████████░░░░  85% Strong  │
│  Moment of Inertia       ███████░░░░░░░░░  60% Moderate│
│  → weakness: forgets ½ factor for disc                  │
│                                                         │
│  Torque                  █████░░░░░░░░░░░  45% WEAK ⚠️  │
│  → weakness: sign convention confusion                  │
│  → error pattern: 60% error rate                        │
│  → next review: Tomorrow                                │
│                                                         │
│  Angular Momentum        ████░░░░░░░░░░░░  30% Weak    │
│  Conservation Laws       ░░░░░░░░░░░░░░░░  0%  New     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. Daily Briefing (The "Daily Calm")

```
┌─────────────────────────────────────────────────────────┐
│  Wednesday, April 2 | 🔋 Energy: Medium | Focus: Physics│
├─────────────────────────────────────────────────────────┤
│  🎯 TODAY'S MISSION (3 tasks)                           │
│                                                         │
│  1. Fix Torque Signs [15 min] ⚠️ HIGH PRIORITY          │
│     ↳ You keep mixing these up                          │
│     ↳ Micro-lesson ready                                │
│     [Start Now]                                         │
│                                                         │
│  2. School HW - NCERT Page 48 Q5-10 [45 min]            │
│     ↳ Due tomorrow                                      │
│     ↳ Uses same sign rules                              │
│     [Locked until Task 1 done]                          │
│                                                         │
│  3. PW Class: Rotational Dynamics [90 min]              │
│     ↳ 4:00 PM | Don't miss                              │
│     ↳ New topic: Angular Momentum                       │
│     [Remind me 15 min before]                           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📊 YOUR STATE                                          │
│  Rotational: 62% ↗ (+5% this week)                      │
│  Torque: 45% ⚠️ (working on it)                         │
│  Last error: Similar to 3 days ago                      │
│  Streak: 12 days consistent study 🔥                    │
└─────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Automatic Capture** | Photo → OCR, Voice → Text, WhatsApp → Parsed |
| **Cross-Mapping** | Links NCERT topics to PW lectures automatically |
| **Understanding Model** | Tracks concept mastery, error patterns, learning velocity |
| **Smart Scheduling** | Priority algorithm: Deadline × Overlap × Forgetting × Energy |
| **Stress Detection** | Reduces workload when student is overwhelmed |
| **Offline-First** | Works without internet; syncs when available |

## Tech Stack

### Backend
- **Framework**: Python + FastAPI
- **Database**: PostgreSQL (cloud), SQLite (local)
- **AI/ML**: Custom NLP for parsing, Phi-4/TinyLlama for local inference
- **OCR**: Tesseract / Google ML Kit
- **Voice**: Whisper.cpp

### Mobile
- **Framework**: Flutter
- **State Management**: Provider + BLoC
- **Local Storage**: Hive + SQLite
- **Charts**: fl_chart

## Project Structure

```
setu_system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── core/
│   │   ├── understanding_model.py  # Student learning model
│   │   ├── task_assignment.py      # Task scheduling engine
│   │   └── content_ingestion.py    # PW + School content parsers
│   └── requirements.txt
│
├── mobile/
│   ├── lib/
│   │   ├── main.dart           # Flutter app entry
│   │   ├── models/
│   │   │   └── task_model.dart # Data models with Hive
│   │   ├── screens/
│   │   │   ├── splash_screen.dart
│   │   │   ├── home_screen.dart
│   │   │   ├── daily_brief_screen.dart  # Core feature
│   │   │   ├── capture_screen.dart      # Post-school input
│   │   │   └── progress_screen.dart     # Analytics
│   │   ├── services/
│   │   │   └── offline_storage_service.dart
│   │   ├── widgets/
│   │   │   └── task_card.dart
│   │   └── utils/
│   │       └── theme.dart
│   └── pubspec.yaml
│
├── docs/
│   └── TECHNICAL_SPEC.md       # Detailed technical documentation
│
└── README.md
```

## How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
# API runs at http://localhost:8000
```

### Mobile
```bash
cd mobile
flutter pub get
flutter run
```

### Demo Data
```bash
# Create demo student (Aarav)
curl -X POST http://localhost:8000/demo/setup
```

## API Examples

### Get Daily Brief
```bash
curl http://localhost:8000/daily-brief/{student_id}
```

### Capture School Session
```bash
curl -X POST http://localhost:8000/capture \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "stu_...",
    "quick_text": "Today sir taught Rotational Motion. Page 48 ke 5 numericals diye hai."
  }'
```

### Complete Task
```bash
curl -X POST http://localhost:8000/tasks/complete \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task_...",
    "student_id": "stu_...",
    "score": 0.7,
    "errors": ["Sign convention confusion"],
    "time_taken_minutes": 50
  }'
```

## The Impact

For students like Aarav:

| Before Setu | After Setu |
|-------------|------------|
| 30 min daily planning | 2 min morning brief |
| Missed deadlines | Zero missed deadlines |
| Random question solving | Optimized, achievable targets |
| Stress level: 8/10 | Stress level: 4/10 |
| Sleep: 11:30 PM | Sleep: 10:30 PM |

## Future Roadmap

1. **Phase 1**: Core daily brief + capture (MVP)
2. **Phase 2**: Advanced analytics + parent dashboard
3. **Phase 3**: Peer learning + doubt resolution
4. **Phase 4**: AI tutor integration

---

**Built for Bharat 🇮🇳**

*"You don't need another teacher. You need one trusted friend who knows everything being asked of you, and only shows you what matters right now."*
