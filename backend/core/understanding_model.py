"""
Setu Core - Student Understanding Model
Builds and maintains a dynamic model of what the student knows
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import math

from models.schemas import (
    StudentState, ConceptMasteryState, ErrorRecord, ConceptMastery,
    Task, Question, ErrorType, StressLevel
)


class UnderstandingModelEngine:
    """
    Core engine for building and updating the student understanding model.
    Tracks concept mastery, error patterns, and learning velocity.
    """
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.concepts: Dict[str, ConceptMasteryState] = {}
        self.errors: List[ErrorRecord] = []
        self.session_history: List[Dict] = []
        
    def record_task_completion(
        self,
        task: Task,
        score: Optional[float],
        errors: List[str],
        time_taken_minutes: int
    ) -> ConceptMasteryState:
        """
        Update understanding model based on task completion.
        Returns updated state for primary concept.
        """
        primary_concept = task.concepts_targeted[0] if task.concepts_targeted else None
        if not primary_concept:
            return None
            
        # Get or create concept state
        if primary_concept not in self.concepts:
            self.concepts[primary_concept] = ConceptMasteryState(
                concept_id=primary_concept,
                first_seen=date.today()
            )
        
        state = self.concepts[primary_concept]
        state.exposure_count += 1
        state.last_tested = date.today()
        
        # Update performance metrics
        if score is not None:
            # Weighted average: recent performance matters more
            old_weight = 0.6
            state.correct_application_rate = (
                old_weight * state.correct_application_rate + 
                (1 - old_weight) * score
            )
        
        # Record errors
        for error in errors:
            self._record_error(primary_concept, task, error, time_taken_minutes)
        
        # Update mastery level
        state.mastery_level = self._calculate_mastery_level(state)
        
        # Schedule next review (spaced repetition)
        state.next_review_due = self._calculate_next_review(state)
        
        return state
    
    def _record_error(
        self,
        concept_id: str,
        task: Task,
        error_description: str,
        time_taken: int
    ) -> ErrorRecord:
        """Record and analyze an error"""
        
        # Classify error type
        error_type = self._classify_error(error_description)
        
        # Find similar past errors
        similar_errors = [
            e.id for e in self.errors
            if e.concept_id == concept_id and e.error_type == error_type
        ]
        
        error_record = ErrorRecord(
            id=f"ERR_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.errors)}",
            timestamp=datetime.now(),
            student_id=self.student_id,
            concept_id=concept_id,
            source_type=task.content_type,
            source_id=task.source_id or "",
            question_number=0,  # Extract from task if available
            difficulty="medium",
            error_type=error_type,
            specific_mistake=error_description,
            root_cause=self._infer_root_cause(error_description, concept_id),
            time_spent_minutes=time_taken,
            hints_used=0,  # Track if we add hint system
            final_outcome="wrong",
            similar_past_errors=similar_errors[-3:]  # Last 3 similar errors
        )
        
        self.errors.append(error_record)
        
        # Update concept state with error info
        state = self.concepts.get(concept_id)
        if state:
            state.error_count += 1
            if error_type.value not in state.error_patterns:
                state.error_patterns.append(error_type.value)
            
            # Extract specific weakness
            weakness = self._extract_weakness(error_description)
            if weakness and weakness not in state.specific_weaknesses:
                state.specific_weaknesses.append(weakness)
        
        return error_record
    
    def _classify_error(self, error_description: str) -> ErrorType:
        """Classify error based on description"""
        error_lower = error_description.lower()
        
        if any(w in error_lower for w in ["sign", "positive", "negative", "direction"]):
            return ErrorType.SIGN_CONVENTION
        elif any(w in error_lower for w in ["unit", "convert", "m/s", "km/h"]):
            return ErrorType.UNIT_CONVERSION
        elif any(w in error_lower for w in ["formula", "equation", "substitute"]):
            return ErrorType.FORMULA
        elif any(w in error_lower for w in ["calculation", "arithmetic", "multiply", "divide"]):
            return ErrorType.CALCULATION
        elif any(w in error_lower for w in ["understand", "concept", "confused"]):
            return ErrorType.CONCEPTUAL
        elif any(w in error_lower for w in ["read", "misread", "question"]):
            return ErrorType.READING
        else:
            return ErrorType.CARELESS
    
    def _infer_root_cause(self, error_description: str, concept_id: str) -> Optional[str]:
        """Infer the root cause of an error"""
        error_type = self._classify_error(error_description)
        
        root_causes = {
            ErrorType.SIGN_CONVENTION: "Mixed school method with PW method - sign convention confusion",
            ErrorType.UNIT_CONVERSION: "Weak in dimensional analysis - needs practice",
            ErrorType.FORMULA: "Formula recall issue - needs spaced repetition",
            ErrorType.CALCULATION: "Careless calculation - check work habit needed",
            ErrorType.CONCEPTUAL: "Fundamental concept gap - requires re-teaching",
        }
        
        return root_causes.get(error_type)
    
    def _extract_weakness(self, error_description: str) -> Optional[str]:
        """Extract specific weakness from error"""
        # Pattern matching for common weaknesses
        patterns = {
            "sign": "sign_convention_confusion",
            "torque": "torque_application",
            "axis": "axis_selection",
            "integration": "integration_visualization",
            "moment of inertia": "moment_of_inertia_calculation",
            "free body": "free_body_diagram",
        }
        
        error_lower = error_description.lower()
        for pattern, weakness in patterns.items():
            if pattern in error_lower:
                return weakness
        return None
    
    def _calculate_mastery_level(self, state: ConceptMasteryState) -> ConceptMastery:
        """Calculate mastery level based on performance metrics"""
        if state.exposure_count == 0:
            return ConceptMastery.NOT_STARTED
        
        rate = state.correct_application_rate
        errors = state.error_count
        exposures = state.exposure_count
        
        error_rate = errors / max(exposures, 1)
        
        if rate >= 0.9 and error_rate < 0.1:
            return ConceptMastery.MASTERED
        elif rate >= 0.75:
            return ConceptMastery.STRONG
        elif rate >= 0.5:
            return ConceptMastery.MODERATE
        else:
            return ConceptMastery.WEAK
    
    def _calculate_next_review(self, state: ConceptMasteryState) -> date:
        """Calculate next review date using spaced repetition"""
        base_intervals = {
            ConceptMastery.NOT_STARTED: 1,
            ConceptMastery.WEAK: 1,
            ConceptMastery.MODERATE: 3,
            ConceptMastery.STRONG: 7,
            ConceptMastery.MASTERED: 14
        }
        
        base_days = base_intervals.get(state.mastery_level, 3)
        
        # Adjust based on error rate
        error_rate = state.error_count / max(state.exposure_count, 1)
        if error_rate > 0.5:
            base_days = max(1, base_days // 2)  # Review sooner if many errors
        
        return date.today() + timedelta(days=base_days)
    
    def get_weak_areas(self, limit: int = 5) -> List[Tuple[str, ConceptMasteryState]]:
        """Get student's weakest areas for targeted practice"""
        weak_concepts = [
            (cid, state) for cid, state in self.concepts.items()
            if state.mastery_level in [ConceptMastery.WEAK, ConceptMastery.NOT_STARTED]
        ]
        
        # Sort by confidence score (lowest first)
        weak_concepts.sort(key=lambda x: x[1].confidence_score)
        
        return weak_concepts[:limit]
    
    def get_recommended_review_topics(self) -> List[str]:
        """Get topics due for review based on spaced repetition"""
        today = date.today()
        review_topics = [
            cid for cid, state in self.concepts.items()
            if state.next_review_due and state.next_review_due <= today
        ]
        return review_topics
    
    def predict_performance(
        self,
        concept_id: str,
        question_difficulty: str
    ) -> Tuple[float, str]:
        """
        Predict probability of correct answer and provide insight.
        Returns: (probability, insight_message)
        """
        state = self.concepts.get(concept_id)
        if not state:
            return 0.5, "New concept - no prediction available"
        
        base_prob = state.correct_application_rate
        
        # Adjust for difficulty
        difficulty_adjustment = {
            "easy": 0.15,
            "medium": 0.0,
            "hard": -0.15
        }
        adjustment = difficulty_adjustment.get(question_difficulty, 0)
        
        # Adjust for error patterns
        if state.error_patterns:
            adjustment -= 0.05 * len(state.error_patterns)
        
        predicted_prob = max(0.1, min(0.95, base_prob + adjustment))
        
        # Generate insight
        if predicted_prob < 0.4:
            insight = f"High risk area - {state.specific_weaknesses[0] if state.specific_weaknesses else 'review needed'}"
        elif predicted_prob < 0.7:
            insight = "Moderate confidence - watch for common errors"
        else:
            insight = "Good chance of success - maintain focus"
        
        return predicted_prob, insight
    
    def calculate_stress_level(
        self,
        pending_tasks: int,
        overdue_tasks: int,
        recent_completion_rate: float
    ) -> StressLevel:
        """Calculate current stress level"""
        if overdue_tasks > 3 or recent_completion_rate < 0.3:
            return StressLevel.CRISIS
        elif overdue_tasks > 0 or recent_completion_rate < 0.5:
            return StressLevel.AT_RISK
        elif pending_tasks > 10 or recent_completion_rate < 0.7:
            return StressLevel.ELEVATED
        elif pending_tasks > 5:
            return StressLevel.NORMAL
        else:
            return StressLevel.CALM
    
    def generate_learning_insights(self) -> List[str]:
        """Generate personalized insights for the student"""
        insights = []
        
        # Error pattern insights
        error_types = defaultdict(int)
        for error in self.errors[-20:]:  # Last 20 errors
            error_types[error.error_type.value] += 1
        
        if error_types:
            most_common = max(error_types.items(), key=lambda x: x[1])
            if most_common[1] >= 3:
                insights.append(
                    f"Pattern detected: {most_common[0]} errors ({most_common[1]} times). "
                    "Focus on careful checking."
                )
        
        # Mastery insights
        weak_areas = self.get_weak_areas(3)
        if weak_areas:
            concepts = ", ".join([c[0] for c in weak_areas])
            insights.append(f"Priority focus areas: {concepts}")
        
        # Progress insights
        mastered_count = sum(
            1 for s in self.concepts.values()
            if s.mastery_level == ConceptMastery.MASTERED
        )
        if mastered_count > 0:
            insights.append(f"Great job! {mastered_count} concepts mastered so far.")
        
        return insights
    
    def export_state(self) -> StudentState:
        """Export current state for API response"""
        # Calculate completion rate from recent history
        recent_completion_rate = 0.8  # Default, calculate from actual data
        
        return StudentState(
            student_id=self.student_id,
            updated_at=datetime.now(),
            concept_mastery=self.concepts,
            theory_absorption_speed="medium",
            numerical_speed="medium",
            revision_need="medium",
            average_homework_duration_minutes=45,
            last_week_completion_rate=recent_completion_rate,
            late_submissions=0,
            help_seeking_frequency="stable",
            current_stress_level=StressLevel.NORMAL
        )
