# Setu - The Bridge Agent for Hybrid Learners

> "Bridging the gap between school (NCERT) and competitive exam prep (Physics Wallah)"

## Overview

Setu is an AI-powered educational assistant designed for students like Aarav - high achievers in rural India who are juggling traditional CBSE schooling with online competitive exam preparation through platforms like Physics Wallah.

## Core Problem Solved

Students living in "two disconnected learning systems":
- **School**: Chalkboard, NCERT textbooks, manual notes, weekly tests
- **Online Prep**: Digital lectures, DPPs (Daily Practice Problems), module questions, mock tests

The cognitive load of translating between these systems is exhausting and error-prone.

## Key Features

### 1. Automatic Content Ingestion
- **PW Integration**: Auto-fetch lectures, DPPs, modules, test schedules via API
- **School Capture**: Photo → OCR → Structured notes from blackboard/notebook
- **WhatsApp Parsing**: Auto-extract homework from class group messages
- **Voice Input**: Hindi/English transcription for quick logging

### 2. Cross-Curriculum Mapping
- Maps NCERT chapters to PW lectures
- Identifies overlap: "School Q3 = DPP Q7 (modified numbers)"
- Unified learning graph instead of separate tracks

### 3. Student Understanding Model
- Tracks concept mastery per topic
- Error pattern analysis (e.g., "sign convention confusion - 60% error rate")
- Predictive learning velocity
- Spaced repetition scheduling

### 4. Intelligent Task Assignment
- Priority algorithm: Deadline × Syllabus Overlap × Forgetting Curve × Energy Match
- Hides queue depth - shows only what matters today
- Auto-adjusts based on performance

### 5. Daily Briefing
- Morning 2-minute summary
- "Must Do" vs "Queued" vs "Done" buckets
- Stress detection and intervention

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SETU SYSTEM                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ FETCHER  │→ │ PARSER   │→ │ MAPPER   │→ │ TASKER   │   │
│  │ Agent    │  │ Agent    │  │ Agent    │  │ Agent    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       ↓             ↓             ↓             ↓           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           UNDERSTANDING MODEL (Graph DB)            │  │
│  │         "What Aarav Knows & What He Needs"          │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  FLUTTER APP (Offline-First)                                │
│  • Daily Brief Screen    • Task Manager    • Capture Flow   │
│  • Progress Dashboard    • Stress Mode     • Family View    │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend API | Python + FastAPI |
| Database | SQLite (local) + PostgreSQL (cloud sync) |
| Mobile App | Flutter |
| OCR | ML Kit (on-device) |
| Voice | Whisper.cpp (tiny) |
| Local LLM | Phi-4 / TinyLlama |
| Sync | Firebase (differential, <50KB/day) |

## Project Structure

```
setu_system/
├── backend/           # FastAPI server
│   ├── api/          # REST endpoints
│   ├── core/         # Business logic
│   ├── models/       # Pydantic models
│   └── services/     # External integrations
├── mobile/           # Flutter app
│   ├── lib/
│   │   ├── screens/  # UI screens
│   │   ├── services/ # Local services
│   │   └── models/   # Data models
│   └── assets/       # Images, fonts
├── ai_models/        # Local AI models
│   ├── whisper/      # Voice transcription
│   └── llm/          # Phi-4 / TinyLlama
└── docs/             # Documentation
```

## Getting Started

### Prerequisites
- Python 3.10+
- Flutter 3.0+
- 8GB RAM minimum (for local LLM)

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Mobile Setup
```bash
cd mobile
flutter pub get
flutter run
```

## License
MIT License - Built for Bharat 🇮🇳
