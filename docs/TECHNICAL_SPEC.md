# Setu Technical Specification

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              SETU SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         BACKEND (Python/FastAPI)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │   FETCHER   │  │   PARSER    │  │      MAPPER             │  │   │
│  │  │   Agent     │→ │   Agent     │→ │   (Cross-Curriculum)    │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  │         ↓                ↓                    ↓                  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │              UNDERSTANDING MODEL ENGINE                    │  │   │
│  │  │  • Concept Mastery Tracking                               │  │   │
│  │  │  • Error Pattern Analysis                                 │  │   │
│  │  │  • Spaced Repetition Scheduling                           │  │   │
│  │  │  • Performance Prediction                                 │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  │                              ↓                                  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │              TASK ASSIGNMENT ENGINE                        │  │   │
│  │  │  • Priority Algorithm                                     │  │   │
│  │  │  • Deadline Management                                    │  │   │
│  │  │  • Energy Matching                                        │  │   │
│  │  │  • Stress Detection                                       │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓ REST API                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      MOBILE APP (Flutter)                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ Daily Brief │  │   Capture   │  │      Progress           │  │   │
│  │  │   Screen    │  │   Screen    │  │       Screen            │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────────────────────┐  │   │
│  │  │              OFFLINE STORAGE (Hive/SQLite)                 │  │   │
│  │  │  • Tasks  • Briefs  • Profile  • Concepts  • Sync Queue   │  │   │
│  │  └───────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Algorithms

### 1. Priority Score Calculation

```python
def calculate_priority_score(item, target_date):
    """
    Priority = 0.40 * Deadline + 0.35 * Syllabus Overlap + 0.20 * Forgetting Curve + 0.05 * Energy Match
    """
    
    # Factor 1: Deadline urgency (40%)
    days_until = (item.deadline - target_date).days
    deadline_score = deadline_urgency_map(days_until)
    
    # Factor 2: Syllabus overlap (35%)
    overlap_score = calculate_syllabus_overlap(item)
    
    # Factor 3: Forgetting curve (20%)
    forgetting_score = calculate_review_priority(item)
    
    # Factor 4: Energy match (5%)
    energy_score = match_energy_level(item.difficulty)
    
    return 0.40 * deadline_score + 0.35 * overlap_score + 0.20 * forgetting_score + 0.05 * energy_score
```

### 2. Spaced Repetition

```python
def calculate_next_review(state):
    """
    Base intervals based on mastery level:
    - Not Started: 1 day
    - Weak: 1 day
    - Moderate: 3 days
    - Strong: 7 days
    - Mastered: 14 days
    
    Adjusted by error rate:
    - Error rate > 50%: Review sooner (interval // 2)
    """
    base_intervals = {
        'not_started': 1,
        'weak': 1,
        'moderate': 3,
        'strong': 7,
        'mastered': 14
    }
    
    base = base_intervals[state.mastery_level]
    error_rate = state.error_count / max(state.exposure_count, 1)
    
    if error_rate > 0.5:
        base = max(1, base // 2)
    
    return today + timedelta(days=base)
```

### 3. Error Classification

```python
def classify_error(error_description):
    """
    Classify errors into types for pattern detection:
    - SIGN_CONVENTION: "sign", "positive", "negative", "direction"
    - UNIT_CONVERSION: "unit", "convert", "m/s", "km/h"
    - FORMULA: "formula", "equation", "substitute"
    - CALCULATION: "calculation", "arithmetic", "multiply", "divide"
    - CONCEPTUAL: "understand", "concept", "confused"
    - READING: "read", "misread", "question"
    - CARELESS: default
    """
    patterns = {
        'sign_convention': ['sign', 'positive', 'negative', 'direction'],
        'unit_conversion': ['unit', 'convert', 'm/s', 'km/h'],
        'formula': ['formula', 'equation', 'substitute'],
        'calculation': ['calculation', 'arithmetic', 'multiply', 'divide'],
        'conceptual': ['understand', 'concept', 'confused'],
        'reading': ['read', 'misread', 'question'],
    }
    
    for error_type, keywords in patterns.items():
        if any(kw in error_description.lower() for kw in keywords):
            return error_type
    
    return 'careless'
```

## API Endpoints

### Student Management
```
POST   /students              # Create new student
GET    /students/{id}         # Get student profile
```

### Content Capture
```
POST   /capture               # Process school session capture
       Body: {
         student_id: string,
         blackboard_photo?: base64,
         voice_note?: base64,
         quick_text?: string
       }
```

### Daily Briefing
```
GET    /daily-brief/{id}      # Get morning briefing
       Response: {
         date: Date,
         energy_level: "low" | "medium" | "high",
         must_do: Task[],
         queued: Task[],
         done: Task[],
         weak_areas_today: string[],
         streak_days: number
       }
```

### Task Management
```
POST   /tasks/complete        # Mark task complete
       Body: {
         task_id: string,
         score?: number (0-1),
         errors?: string[],
         time_taken_minutes: number
       }
```

### Understanding Model
```
GET    /understanding/{id}           # Get full understanding model
GET    /understanding/{id}/weak-areas # Get weak areas
GET    /understanding/{id}/predict/{concept} # Predict performance
```

### Cross-Curriculum Mapping
```
GET    /mapping/school-to-pw?topic={topic}  # Map school topic to PW
GET    /mapping/unified-schedule/{id}       # Get unified schedule
```

## Data Models

### Student Understanding Graph

```
Concept Node (e.g., "Moment of Inertia")
├── Prerequisites
│   ├── "Circular Motion" (mastered: 85%)
│   ├── "Torque" (mastered: 60% - WEAK)
│   └── "Integration Basics" (mastered: 70%)
├── NCERT Properties
│   ├── Chapter: "System of Particles"
│   ├── Page Range: "141-175"
│   └── Board Weightage: 8%
├── PW Properties
│   ├── Lecture ID: "PHY_11_08"
│   ├── Lecture Date: "2026-03-28"
│   ├── DPPs: ["DPP_08", "DPP_09"]
│   └── JEE Weightage: 12%
├── Cross-Links
│   ├── "School Q3 = DPP Q7 (modified numbers)"
│   └── "NCERT derivation skips step 3 of JEE proof"
└── Student State
    ├── Exposure Count: 3
    ├── Correct Rate: 60%
    ├── Confidence: 55%
    ├── Error Patterns: ["sign_convention", "formula_recall"]
    └── Next Review: "2026-04-02"
```

### Error Record Schema

```json
{
  "error_id": "ERR_2026_03_29_001",
  "timestamp": "2026-03-29T19:45:00",
  "context": {
    "source": "DPP_PHY_RD_12",
    "question_number": 8,
    "concept_node": "Torque",
    "difficulty": "Medium"
  },
  "error_type": "SIGN_CONVENTION",
  "specific_mistake": "Used clockwise positive instead of anticlockwise",
  "root_cause": "Mixed school method with PW method",
  "time_spent_minutes": 12,
  "hints_used": 2,
  "final_outcome": "WRONG",
  "similar_past_errors": ["ERR_2026_03_25_003"]
}
```

## Offline-First Architecture

### Sync Strategy

1. **Local-First Operations**
   - All writes go to local Hive/SQLite first
   - Background sync to server when online
   - Sync queue maintains order of operations

2. **Conflict Resolution**
   - Server wins for shared data
   - Last-write-wins for personal data
   - Manual merge for critical conflicts

3. **Data Usage**
   - Target: < 100 MB/month
   - Differential sync only
   - Image compression for uploads

### Storage Schema

```dart
// Hive Boxes
Box<Task> tasksBox;           // All tasks
Box<DailyBrief> briefsBox;    // Daily briefs
Box<StudentProfile> profileBox;  // User profile
Box<ConceptMastery> conceptsBox; // Concept states
Box syncQueueBox;             // Pending sync operations
```

## Security Considerations

1. **Data Privacy**
   - Student data encrypted at rest
   - No PII shared with third parties
   - Local processing where possible

2. **API Security**
   - JWT authentication
   - Rate limiting
   - Input validation

3. **Offline Security**
   - Local database encryption
   - Secure key storage

## Performance Targets

| Metric | Target |
|--------|--------|
| App Launch | < 2 seconds |
| Daily Brief Generation | < 1 second |
| OCR Processing | < 3 seconds |
| Task List Load | < 500ms |
| API Response | < 200ms |
| Offline Functionality | 100% |

## Scalability

### Backend Scaling
- Stateless API servers
- Horizontal scaling with load balancer
- Redis for session/cache
- PostgreSQL read replicas

### Mobile Optimization
- Lazy loading for lists
- Image caching
- Background prefetching
- Battery-aware sync

## Monitoring

### Key Metrics
- Daily Active Users (DAU)
- Task Completion Rate
- Average Session Duration
- Sync Success Rate
- Error Rates by Type

### Alerts
- API error rate > 5%
- Sync failure rate > 10%
- Database connection issues
- Memory usage > 80%

## Future Enhancements

1. **AI Features**
   - Local LLM for doubt resolution
   - Predictive stress detection
   - Personalized learning paths

2. **Social Features**
   - Peer comparison (anonymized)
   - Study groups
   - Mentor matching

3. **Platform Expansion**
   - Web dashboard for parents
   - Teacher interface
   - School analytics

4. **Integration**
   - Official PW API
   - NCERT digital textbooks
   - Google Classroom
   - WhatsApp Business API
