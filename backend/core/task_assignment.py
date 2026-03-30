"""
Setu Core - Task Assignment Engine
Intelligent task scheduling based on student state, deadlines, and learning priorities
"""

from datetime import datetime, date, timedelta, time
from typing import List, Dict, Optional, Tuple
import math

from models.schemas import (
    Task, TaskPriority, TaskStatus, StudentState, ConceptMasteryState,
    DPPContent, SchoolSession, StudentProfile, DailyBrief, StressLevel
)
from core.understanding_model import UnderstandingModelEngine


class TaskAssignmentEngine:
    """
    Core engine for assigning and scheduling tasks.
    Implements the priority algorithm that balances:
    - Deadline proximity
    - Syllabus overlap (school + PW)
    - Spaced repetition needs
    - Energy matching
    """
    
    def __init__(
        self,
        student_profile: StudentProfile,
        understanding_model: UnderstandingModelEngine
    ):
        self.profile = student_profile
        self.understanding = understanding_model
        self.tasks: Dict[str, Task] = {}
        
    def generate_daily_tasks(
        self,
        target_date: date,
        pw_schedule: List[DPPContent],
        school_sessions: List[SchoolSession]
    ) -> DailyBrief:
        """
        Generate daily briefing with prioritized tasks.
        This is the core algorithm that replaces manual planning.
        """
        
        # Step 1: Collect all pending items
        pending_items = self._collect_pending_items(pw_schedule, school_sessions)
        
        # Step 2: Calculate priority scores
        scored_items = []
        for item in pending_items:
            score = self._calculate_priority_score(item, target_date)
            scored_items.append((item, score))
        
        # Step 3: Sort by priority score
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        # Step 4: Categorize into buckets
        must_do = []
        queued = []
        
        available_minutes = self._calculate_available_study_time(target_date)
        used_minutes = 0
        
        for item, score in scored_items:
            task = self._create_task_from_item(item, target_date)
            
            if used_minutes + task.estimated_duration_minutes <= available_minutes * 0.8:
                # Top priority items that fit in schedule
                if score > 0.7 or task.deadline == target_date:
                    task.priority = TaskPriority.HIGH
                    must_do.append(task)
                else:
                    task.priority = TaskPriority.MEDIUM
                    queued.append(task)
                used_minutes += task.estimated_duration_minutes
            else:
                # Doesn't fit - queue for later
                task.priority = TaskPriority.LOW
                queued.append(task)
        
        # Step 5: Add intervention tasks if needed
        intervention = self._generate_intervention_task(target_date)
        if intervention:
            must_do.insert(0, intervention)
        
        # Step 6: Calculate state summary
        progress = self._calculate_subject_progress()
        weak_areas = [c[0] for c in self.understanding.get_weak_areas(3)]
        
        # Step 7: Check stress level
        stress_alert = None
        if self.understanding.export_state().current_stress_level == StressLevel.AT_RISK:
            stress_alert = "High workload detected. Consider deferring non-urgent tasks."
        
        return DailyBrief(
            date=target_date,
            student_id=self.profile.id,
            generated_at=datetime.now(),
            energy_level=self._estimate_energy_level(target_date),
            focus_subject=self._determine_focus_subject(must_do),
            must_do=must_do,
            queued=queued,
            done=[],  # Populated during the day
            overall_progress=progress,
            weak_areas_today=weak_areas,
            streak_days=self._calculate_streak(),
            stress_alert=stress_alert,
            deadline_warnings=self._get_deadline_warnings(pending_items, target_date)
        )
    
    def _collect_pending_items(
        self,
        pw_schedule: List[DPPContent],
        school_sessions: List[SchoolSession]
    ) -> List[Dict]:
        """Collect all pending work items from various sources"""
        items = []
        
        # PW DPPs
        for dpp in pw_schedule:
            items.append({
                "type": "dpp",
                "id": dpp.id,
                "title": f"DPP {dpp.id}",
                "concepts": dpp.concepts_tested,
                "estimated_minutes": dpp.estimated_time_minutes,
                "deadline": dpp.release_date + timedelta(days=2),  # 2 days to complete
                "source": "pw",
                "difficulty": "mixed"
            })
        
        # School homework
        for session in school_sessions:
            if session.homework_text:
                items.append({
                    "type": "school_homework",
                    "id": f"school_{session.id}",
                    "title": f"School: {session.homework_text[:30]}...",
                    "concepts": [session.topic_detected],
                    "estimated_minutes": 45,  # Default
                    "deadline": session.deadline or (session.date + timedelta(days=1)),
                    "source": "school",
                    "difficulty": "medium"
                })
        
        # Review items (spaced repetition)
        review_topics = self.understanding.get_recommended_review_topics()
        for topic in review_topics[:3]:  # Max 3 review items per day
            items.append({
                "type": "revision",
                "id": f"review_{topic}",
                "title": f"Review: {topic}",
                "concepts": [topic],
                "estimated_minutes": 20,
                "deadline": date.today(),
                "source": "review",
                "difficulty": "review"
            })
        
        return items
    
    def _calculate_priority_score(
        self,
        item: Dict,
        target_date: date
    ) -> float:
        """
        Calculate priority score (0-1) based on multiple factors:
        - Deadline urgency (40%)
        - Syllabus overlap with school (35%)
        - Forgetting curve (20%)
        - Energy match (5%)
        """
        
        # Factor 1: Deadline urgency
        days_until_deadline = (item["deadline"] - target_date).days
        if days_until_deadline <= 0:
            deadline_score = 1.0  # Overdue
        elif days_until_deadline == 1:
            deadline_score = 0.9
        elif days_until_deadline <= 3:
            deadline_score = 0.7
        elif days_until_deadline <= 7:
            deadline_score = 0.5
        else:
            deadline_score = 0.3
        
        # Factor 2: Syllabus overlap
        overlap_score = self._calculate_syllabus_overlap(item)
        
        # Factor 3: Forgetting curve (review priority)
        forgetting_score = 0.5
        if item["type"] == "revision":
            forgetting_score = 0.8
        elif item["concepts"]:
            # Check if concept is weak
            concept_id = item["concepts"][0]
            state = self.understanding.concepts.get(concept_id)
            if state:
                if state.mastery_level.value in ["weak", "not_started"]:
                    forgetting_score = 0.9
                elif state.next_review_due and state.next_review_due <= target_date:
                    forgetting_score = 0.8
        
        # Factor 4: Energy match
        energy_score = self._calculate_energy_match(item)
        
        # Weighted combination
        final_score = (
            0.40 * deadline_score +
            0.35 * overlap_score +
            0.20 * forgetting_score +
            0.05 * energy_score
        )
        
        return min(1.0, max(0.0, final_score))
    
    def _calculate_syllabus_overlap(self, item: Dict) -> float:
        """
        Calculate overlap between item and current school syllabus.
        High overlap = do together for efficiency.
        """
        if not item["concepts"]:
            return 0.5
        
        # Check if this concept is being taught in school now
        concept_id = item["concepts"][0]
        state = self.understanding.concepts.get(concept_id)
        
        if state and state.last_tested:
            days_since_school = (date.today() - state.last_tested).days
            if days_since_school <= 2:
                return 1.0  # Just taught in school - high priority
            elif days_since_school <= 7:
                return 0.8
        
        # Check if concept appears in recent school sessions
        # (would need school session data)
        if item["source"] == "school":
            return 0.9
        
        return 0.5
    
    def _calculate_energy_match(self, item: Dict) -> float:
        """Match task difficulty to expected energy level"""
        difficulty = item.get("difficulty", "medium")
        
        # Simple mapping - could be more sophisticated
        energy_map = {
            "easy": 0.3,
            "medium": 0.5,
            "hard": 0.8,
            "advanced": 1.0,
            "mixed": 0.6,
            "review": 0.2
        }
        
        return energy_map.get(difficulty, 0.5)
    
    def _create_task_from_item(self, item: Dict, target_date: date) -> Task:
        """Create a Task object from a pending item"""
        task_id = f"task_{item['id']}_{target_date.strftime('%Y%m%d')}"
        
        # Generate reason
        reasons = {
            "dpp": "PW practice - maintain pace",
            "school_homework": "School deadline",
            "revision": "Spaced repetition - consolidate learning",
            "micro_lesson": "Gap identified - targeted intervention"
        }
        
        return Task(
            id=task_id,
            student_id=self.profile.id,
            created_at=datetime.now(),
            title=item["title"],
            content_type=item["type"],
            source_id=item["id"],
            scheduled_date=target_date,
            estimated_duration_minutes=item["estimated_minutes"],
            deadline=item["deadline"],
            priority=TaskPriority.MEDIUM,  # Will be updated
            status=TaskStatus.PENDING,
            concepts_targeted=item["concepts"],
            reason=reasons.get(item["type"], "Practice")
        )
    
    def _generate_intervention_task(self, target_date: date) -> Optional[Task]:
        """Generate intervention task for weak areas"""
        weak_areas = self.understanding.get_weak_areas(1)
        
        if not weak_areas:
            return None
        
        concept_id, state = weak_areas[0]
        
        # Only intervene if weak and recently tested
        if state.mastery_level.value != "weak":
            return None
        
        return Task(
            id=f"intervention_{concept_id}_{target_date.strftime('%Y%m%d')}",
            student_id=self.profile.id,
            created_at=datetime.now(),
            title=f"Fix: {concept_id}",
            description=f"You keep making errors here. 15-minute focused practice.",
            content_type="micro_lesson",
            scheduled_date=target_date,
            estimated_duration_minutes=15,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            concepts_targeted=[concept_id],
            reason=f"Error pattern detected: {state.error_patterns[0] if state.error_patterns else 'weak area'}"
        )
    
    def _calculate_available_study_time(self, target_date: date) -> int:
        """Calculate available study minutes for the day"""
        # Base schedule
        school_end = self.profile.school_timing[1]
        study_start = self.profile.study_hours[0]
        study_end = self.profile.study_hours[1]
        
        # Calculate evening study time
        evening_minutes = (
            study_end.hour * 60 + study_end.minute -
            study_start.hour * 60 - study_start.minute
        )
        
        # Subtract PW class time (if applicable)
        pw_class_minutes = 90  # Typical PW class
        
        # Subtract breaks
        break_minutes = 30
        
        available = evening_minutes - pw_class_minutes - break_minutes
        return max(60, available)  # At least 1 hour
    
    def _estimate_energy_level(self, target_date: date) -> str:
        """Estimate energy level for the day"""
        # Could use sleep data, previous day completion, etc.
        recent_completion = self.understanding.export_state().last_week_completion_rate
        
        if recent_completion > 0.8:
            return "high"
        elif recent_completion > 0.5:
            return "medium"
        else:
            return "low"
    
    def _determine_focus_subject(self, must_do_tasks: List[Task]) -> Optional[str]:
        """Determine primary subject focus for the day"""
        if not must_do_tasks:
            return None
        
        # Count by subject (derived from concepts)
        subject_counts = {}
        for task in must_do_tasks:
            for concept in task.concepts_targeted:
                # Extract subject from concept
                subject = concept.split("_")[0] if "_" in concept else "general"
                subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        if subject_counts:
            return max(subject_counts.items(), key=lambda x: x[1])[0]
        return None
    
    def _calculate_streak(self) -> int:
        """Calculate consecutive days of task completion"""
        # Would track from actual completion data
        return 12  # Placeholder
    
    def _get_deadline_warnings(
        self,
        pending_items: List[Dict],
        target_date: date
    ) -> List[str]:
        """Generate deadline warnings"""
        warnings = []
        
        for item in pending_items:
            days_until = (item["deadline"] - target_date).days
            if days_until == 0:
                warnings.append(f"{item['title'][:20]}... due TODAY")
            elif days_until == 1:
                warnings.append(f"{item['title'][:20]}... due TOMORROW")
        
        return warnings[:3]  # Max 3 warnings
    
    def adjust_for_stress(self, brief: DailyBrief) -> DailyBrief:
        """Adjust task list if student is stressed"""
        if not brief.stress_alert:
            return brief
        
        # Reduce workload
        if len(brief.must_do) > 3:
            # Move non-urgent tasks to queued
            urgent = [t for t in brief.must_do if t.deadline == brief.date]
            non_urgent = [t for t in brief.must_do if t.deadline != brief.date]
            
            brief.must_do = urgent[:3]  # Max 3 urgent tasks
            brief.queued = non_urgent + brief.queued
        
        # Add "Bhai, Chill" task
        brief.must_do.insert(0, Task(
            id=f"chill_{brief.date}",
            student_id=brief.student_id,
            created_at=datetime.now(),
            title="Take a breath",
            description="30 seconds of deep breathing. You've got this.",
            content_type="micro_lesson",
            scheduled_date=brief.date,
            estimated_duration_minutes=1,
            priority=TaskPriority.HIGH,
            status=TaskStatus.PENDING,
            reason="Stress management"
        ))
        
        return brief
