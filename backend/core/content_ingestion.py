"""
Setu Core - Content Ingestion Engine
Automatically fetches and parses content from PW and school sources
"""

import re
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import base64
from io import BytesIO

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from models.schemas import (
    DPPContent, Question, QuestionType, SchoolSession, 
    CaptureInput, CaptureResult, ContentSource
)


class PWContentFetcher:
    """
    Fetches content from Physics Wallah platform.
    In production, this would use official APIs or scraping.
    """
    
    def __init__(self, batch_code: str):
        self.batch_code = batch_code
        self.base_url = "https://www.pw.live"  # Placeholder
        
    def fetch_annual_schedule(self) -> List[Dict]:
        """Fetch complete annual lecture schedule for the batch"""
        # In production: API call or scrape
        # For now, return mock data structure
        
        # Example: Class 11 Physics schedule
        schedule = []
        topics = [
            ("Physical World", "PHY_11_01", "2026-03-01"),
            ("Units and Measurements", "PHY_11_02", "2026-03-03"),
            ("Motion in a Straight Line", "PHY_11_03", "2026-03-08"),
            ("Motion in a Plane", "PHY_11_04", "2026-03-12"),
            ("Laws of Motion", "PHY_11_05", "2026-03-15"),
            ("Work, Energy and Power", "PHY_11_06", "2026-03-20"),
            ("System of Particles", "PHY_11_07", "2026-03-25"),
            ("Rotational Motion", "PHY_11_08", "2026-03-28"),
            ("Gravitation", "PHY_11_09", "2026-04-02"),
        ]
        
        for topic, lecture_id, lecture_date in topics:
            schedule.append({
                "lecture_id": lecture_id,
                "topic": topic,
                "date": lecture_date,
                "duration_minutes": 90,
                "dpp_released": True,
                "dpp_id": f"DPP_{lecture_id.split('_')[-1]}"
            })
        
        return schedule
    
    def fetch_dpp(self, dpp_id: str) -> DPPContent:
        """Fetch a specific DPP with questions"""
        # In production: API call
        # Return mock DPP for demonstration
        
        questions = self._generate_mock_questions(dpp_id)
        
        return DPPContent(
            id=dpp_id,
            batch_code=self.batch_code,
            release_date=date.today(),
            lecture_id=f"PHY_11_{dpp_id.split('_')[-1]}",
            lecture_topic="Rotational Dynamics",
            total_questions=len(questions),
            questions=questions,
            easy_count=3,
            medium_count=4,
            hard_count=3,
            estimated_time_minutes=45,
            concepts_tested=["Moment of Inertia", "Torque", "Angular Momentum"]
        )
    
    def _generate_mock_questions(self, dpp_id: str) -> List[Question]:
        """Generate mock questions for demonstration"""
        return [
            Question(
                id=f"{dpp_id}_Q1",
                dpp_id=dpp_id,
                text="A disc of mass M and radius R rolls without slipping. Find its moment of inertia about the center.",
                topic_tags=["Moment of Inertia", "Disc"],
                question_type=QuestionType.SINGLE_CORRECT,
                difficulty="easy",
                time_estimate_minutes=5,
                formulas_required=["I_disc = ½MR²"],
                answer="½MR²"
            ),
            Question(
                id=f"{dpp_id}_Q2",
                dpp_id=dpp_id,
                text="A torque of 10 Nm is applied to a wheel with moment of inertia 2 kg·m². Find the angular acceleration.",
                topic_tags=["Torque", "Angular Acceleration"],
                question_type=QuestionType.NUMERICAL,
                difficulty="medium",
                time_estimate_minutes=8,
                formulas_required=["τ = Iα"],
                answer="5 rad/s²"
            ),
            Question(
                id=f"{dpp_id}_Q3",
                dpp_id=dpp_id,
                text="A solid sphere and a hollow sphere of same mass and radius roll down an incline. Which reaches bottom first?",
                topic_tags=["Rolling Motion", "Moment of Inertia"],
                question_type=QuestionType.SINGLE_CORRECT,
                difficulty="hard",
                time_estimate_minutes=12,
                formulas_required=["I_solid = ⅖MR²", "I_hollow = ⅔MR²"],
                answer="Solid sphere"
            ),
        ]


class SchoolContentParser:
    """
    Parses school content from various input sources:
    - Blackboard/Notebook photos (OCR)
    - WhatsApp messages
    - Voice notes
    """
    
    def __init__(self):
        self.ncert_mapping = self._load_ncert_mapping()
        
    def _load_ncert_mapping(self) -> Dict[str, Any]:
        """Load NCERT chapter mapping"""
        return {
            "Laws of Motion": {
                "ncert_chapter": "5",
                "page_range": "90-115",
                "pw_topic": "Laws of Motion",
                "pw_lecture_id": "PHY_11_05"
            },
            "Rotational Motion": {
                "ncert_chapter": "7",
                "page_range": "141-175",
                "pw_topic": "Rotational Dynamics",
                "pw_lecture_id": "PHY_11_08"
            },
            "System of Particles": {
                "ncert_chapter": "6",
                "page_range": "115-141",
                "pw_topic": "Centre of Mass",
                "pw_lecture_id": "PHY_11_07"
            }
        }
    
    def parse_capture(self, capture: CaptureInput) -> CaptureResult:
        """
        Main entry point for processing student capture input.
        Returns structured school session data.
        """
        
        # Try different input methods in order of preference
        if capture.blackboard_photo:
            return self._parse_blackboard_photo(capture)
        elif capture.voice_note:
            return self._parse_voice_note(capture)
        elif capture.quick_text:
            return self._parse_quick_text(capture)
        else:
            return CaptureResult(
                success=False,
                insight="No input provided"
            )
    
    def _parse_blackboard_photo(self, capture: CaptureInput) -> CaptureResult:
        """Parse blackboard/notebook photo using OCR"""
        if not OCR_AVAILABLE:
            return CaptureResult(
                success=False,
                insight="OCR not available - please use voice or text input"
            )
        
        try:
            # Decode base64 image
            image_data = base64.b64decode(capture.blackboard_photo.split(',')[1] 
                                         if ',' in capture.blackboard_photo 
                                         else capture.blackboard_photo)
            image = Image.open(BytesIO(image_data))
            
            # Perform OCR
            text = pytesseract.image_to_string(image, lang='eng+hin')
            
            # Extract structured info
            return self._extract_from_text(text, capture)
            
        except Exception as e:
            return CaptureResult(
                success=False,
                insight=f"OCR failed: {str(e)}"
            )
    
    def _parse_voice_note(self, capture: CaptureInput) -> CaptureResult:
        """Parse voice note using Whisper"""
        # In production: Use Whisper.cpp for local transcription
        # For now, simulate with provided quick_text if available
        
        if capture.quick_text:
            return self._extract_from_text(capture.quick_text, capture)
        
        return CaptureResult(
            success=False,
            insight="Voice transcription not implemented in demo"
        )
    
    def _parse_quick_text(self, capture: CaptureInput) -> CaptureResult:
        """Parse quick text input"""
        text = capture.quick_text or capture.homework_description or ""
        return self._extract_from_text(text, capture)
    
    def _extract_from_text(
        self, 
        text: str, 
        capture: CaptureInput
    ) -> CaptureResult:
        """Extract structured data from text (Hindi or English)"""
        
        # Detect language and normalize
        is_hindi = self._detect_hindi(text)
        
        # Extract topic
        topic = self._extract_topic(text)
        
        # Extract homework
        homework = self._extract_homework(text)
        
        # Extract formulas
        formulas = self._extract_formulas(text)
        
        # Extract key points
        key_points = self._extract_key_points(text)
        
        # Map to NCERT
        ncert_info = self.ncert_mapping.get(topic, {})
        
        # Create session
        session = SchoolSession(
            id=f"session_{capture.timestamp.strftime('%Y%m%d_%H%M%S')}",
            date=capture.timestamp.date(),
            subject="Physics",  # Detect from context
            topic_detected=topic,
            sub_topics=self._extract_sub_topics(text),
            key_points=key_points,
            formulas_written=formulas,
            homework_text=homework.get("text"),
            homework_questions=homework.get("count"),
            page_reference=homework.get("page"),
            deadline=homework.get("deadline"),
            ncert_chapter=ncert_info.get("ncert_chapter"),
            ncert_page_range=ncert_info.get("page_range"),
            pw_overlap_topics=[ncert_info.get("pw_topic", "")] if ncert_info else [],
            pw_lecture_date=None  # Would look up from schedule
        )
        
        # Create homework task if found
        homework_task = None
        if homework.get("text"):
            from models.schemas import Task, TaskPriority
            homework_task = Task(
                id=f"school_hw_{session.id}",
                student_id=capture.student_id,
                created_at=capture.timestamp,
                title=f"School: {homework['text'][:30]}...",
                content_type="school_homework",
                scheduled_date=capture.timestamp.date(),
                estimated_duration_minutes=homework.get("estimated_minutes", 45),
                deadline=homework.get("deadline"),
                priority=TaskPriority.HIGH,
                concepts_targeted=[topic] if topic else []
            )
        
        # Generate insight
        insight = self._generate_insight(session, ncert_info)
        
        return CaptureResult(
            success=True,
            session=session,
            extracted_homework=homework_task,
            pw_matches=[ncert_info.get("pw_topic", "")] if ncert_info else [],
            suggested_dpp_questions=self._suggest_dpp_questions(topic),
            insight=insight
        )
    
    def _detect_hindi(self, text: str) -> bool:
        """Detect if text contains Hindi"""
        hindi_range = range(0x0900, 0x097F)
        return any(ord(c) in hindi_range for c in text)
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text"""
        # Common patterns
        topic_patterns = [
            r"(?:today|aaj)\s+(?:we studied|sir ne|teacher)\s+(.+?)(?:\.|,|padhaya)",
            r"(?:topic|chapter)\s*(?:is|was|:)\s*(.+?)(?:\.|,|$)",
            r"(.+?)\s+(?:padhaya|pada|completed)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Check for known topics
        known_topics = [
            "Laws of Motion", "Rotational Motion", "Gravitation",
            "Work Energy Power", "System of Particles", "Oscillations",
            "Waves", "Thermodynamics", "Kinetic Theory"
        ]
        
        for topic in known_topics:
            if topic.lower() in text.lower():
                return topic
        
        return "Unknown Topic"
    
    def _extract_homework(self, text: str) -> Dict:
        """Extract homework details from text"""
        homework = {"text": None, "count": None, "page": None, "deadline": None}
        
        # Homework patterns (English and Hindi mixed)
        hw_patterns = [
            r"(?:homework|hw|assignment|diya|di)\s*(?:is|:)?\s*(.+?)(?:\.|,|kal|tomorrow)",
            r"(?:page|pg)\s*(\d+)\s*(?:ke|que|questions)?\s*(\d+)\s*(?:questions|que|numericals)?",
            r"(\d+)\s*(?:questions|que|numericals|num)\s*(?:from|of|page|pg)?\s*(?:page|pg)?\s*(\d+)"
        ]
        
        for pattern in hw_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    homework["page"] = match.group(1)
                    homework["count"] = int(match.group(2)) if match.group(2).isdigit() else None
                else:
                    homework["text"] = match.group(1).strip()
        
        # Extract deadline
        if "kal" in text.lower() or "tomorrow" in text.lower():
            homework["deadline"] = date.today() + __import__('datetime').timedelta(days=1)
        elif "day after" in text.lower() or "parso" in text.lower():
            homework["deadline"] = date.today() + __import__('datetime').timedelta(days=2)
        
        # Estimate time
        if homework["count"]:
            homework["estimated_minutes"] = homework["count"] * 8  # ~8 min per question
        
        return homework
    
    def _extract_formulas(self, text: str) -> List[str]:
        """Extract formulas from text"""
        formulas = []
        
        # Formula patterns
        formula_patterns = [
            r"([A-Z]=[^\s,]+)",  # F=ma, τ=Iα
            r"([a-z]=[^\s,]+)",  # a=F/m
            r"([A-Z]\s*=\s*[^\s,]+)"  # F = ma
        ]
        
        for pattern in formula_patterns:
            matches = re.findall(pattern, text)
            formulas.extend(matches)
        
        return list(set(formulas))[:5]  # Max 5 formulas
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points taught"""
        points = []
        
        # Bullet points or numbered lists
        bullet_pattern = r"(?:^|\n)\s*[•\-\*\d\.]+\s*(.+?)(?:\n|$)"
        matches = re.findall(bullet_pattern, text)
        points.extend(matches[:5])
        
        # "Important" markers
        important_pattern = r"(?:important|zaruri|dhyan|note)\s*(?:is|:)?\s*(.+?)(?:\.|,|$)"
        matches = re.findall(important_pattern, text, re.IGNORECASE)
        points.extend(matches[:3])
        
        return points
    
    def _extract_sub_topics(self, text: str) -> List[str]:
        """Extract sub-topics covered"""
        # Look for "and" separated topics or bullet points
        sub_topics = []
        
        # Common sub-topic patterns
        patterns = [
            r"(?:including|covering|covered)\s+(.+?)(?:\.|,|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                topics = match.group(1).split(",")
                sub_topics = [t.strip() for t in topics[:5]]
        
        return sub_topics
    
    def _generate_insight(
        self, 
        session: SchoolSession, 
        ncert_info: Dict
    ) -> str:
        """Generate insight about the session"""
        if not ncert_info:
            return f"Recorded: {session.topic_detected}. No PW match found."
        
        pw_topic = ncert_info.get("pw_topic", "")
        pw_lecture = ncert_info.get("pw_lecture_id", "")
        
        return (
            f"School is teaching '{session.topic_detected}' (NCERT Ch {ncert_info.get('ncert_chapter')}). "
            f"PW covered '{pw_topic}' in lecture {pw_lecture}. "
            f"Use PW notes for deeper understanding, present NCERT-style for homework."
        )
    
    def _suggest_dpp_questions(self, topic: str) -> List[str]:
        """Suggest relevant DPP questions based on topic"""
        # Would query DPP database
        return [f"DPP questions on {topic} - check your batch schedule"]


class CrossCurriculumMapper:
    """
    Maps between NCERT (school) and PW (competitive) curricula.
    Creates the unified learning graph.
    """
    
    def __init__(self):
        self.topic_graph = self._build_topic_graph()
        
    def _build_topic_graph(self) -> Dict[str, Any]:
        """Build the unified topic graph"""
        return {
            "Physics": {
                "Mechanics": {
                    "prerequisites": [],
                    "topics": [
                        "Units and Measurements",
                        "Motion in 1D", "Motion in 2D",
                        "Laws of Motion",
                        "Work, Energy, Power",
                        "Centre of Mass",
                        "Rotational Motion",
                        "Gravitation"
                    ]
                }
            }
        }
    
    def map_school_to_pw(
        self, 
        school_topic: str, 
        school_page: Optional[str]
    ) -> Dict[str, Any]:
        """
        Map a school topic to corresponding PW content.
        Returns PW lecture info, relevant DPPs, etc.
        """
        # Mapping database
        mappings = {
            "Laws of Motion": {
                "pw_lecture_id": "PHY_11_05",
                "pw_lecture_date": "2026-03-15",
                "dpp_ids": ["DPP_05", "DPP_06"],
                "module_sections": ["5.1", "5.2", "5.3"],
                "insight": "PW covered this 15 days ago. DPP 05 Q1-5 are perfect warm-up."
            },
            "Rotational Motion": {
                "pw_lecture_id": "PHY_11_08",
                "pw_lecture_date": "2026-03-28",
                "dpp_ids": ["DPP_08", "DPP_09"],
                "module_sections": ["7.1", "7.2", "7.3", "7.4"],
                "insight": "PW covered this yesterday! School is 1 day behind."
            }
        }
        
        return mappings.get(school_topic, {
            "pw_lecture_id": None,
            "insight": "No direct PW match found. Check module index."
        })
    
    def find_overlap_questions(
        self, 
        school_homework: str, 
        dpp_questions: List[Question]
    ) -> List[Question]:
        """
        Find DPP questions that overlap with school homework.
        Returns questions that practice the same concept.
        """
        # Extract concepts from homework
        homework_concepts = self._extract_concepts(school_homework)
        
        overlapping = []
        for q in dpp_questions:
            # Check if question tests same concepts
            if any(c in homework_concepts for c in q.topic_tags):
                overlapping.append(q)
        
        return overlapping[:5]  # Top 5 matches
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract physics concepts from text"""
        concept_keywords = {
            "force": ["force", "newton", "f=ma"],
            "torque": ["torque", "moment", "rotation"],
            "inertia": ["inertia", "moment of inertia", "i="],
            "momentum": ["momentum", "angular momentum", "impulse"],
            "energy": ["energy", "kinetic", "potential", "work"]
        }
        
        found_concepts = []
        text_lower = text.lower()
        
        for concept, keywords in concept_keywords.items():
            if any(kw in text_lower for kw in keywords):
                found_concepts.append(concept)
        
        return found_concepts
    
    def generate_unified_schedule(
        self,
        school_schedule: List[SchoolSession],
        pw_schedule: List[DPPContent]
    ) -> List[Dict]:
        """
        Generate a unified schedule that integrates both curricula.
        Returns daily learning plan with cross-references.
        """
        unified = []
        
        # Create date-indexed lookup
        school_by_date = {s.date: s for s in school_schedule}
        pw_by_date = {d.release_date: d for d in pw_schedule}
        
        # Get all unique dates
        all_dates = sorted(set(
            list(school_by_date.keys()) + list(pw_by_date.keys())
        ))
        
        for d in all_dates:
            day_plan = {
                "date": d,
                "school": None,
                "pw": None,
                "cross_reference": None
            }
            
            if d in school_by_date:
                day_plan["school"] = school_by_date[d]
            
            if d in pw_by_date:
                day_plan["pw"] = pw_by_date[d]
            
            # Generate cross-reference
            if day_plan["school"] and day_plan["pw"]:
                day_plan["cross_reference"] = self._generate_cross_ref(
                    day_plan["school"], day_plan["pw"]
                )
            
            unified.append(day_plan)
        
        return unified
    
    def _generate_cross_ref(
        self, 
        school: SchoolSession, 
        pw: DPPContent
    ) -> str:
        """Generate cross-reference insight"""
        return (
            f"School: {school.topic_detected} | "
            f"PW: {pw.lecture_topic} | "
            f"DPP: {pw.total_questions} questions"
        )
