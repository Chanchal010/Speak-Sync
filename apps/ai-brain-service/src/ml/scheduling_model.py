"""
ML-powered Scheduling Model
Uses pattern recognition and predictive analytics for intelligent task scheduling
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict, Counter
import json


class SchedulingModel:
    """
    Machine Learning model for intelligent task scheduling
    Uses historical data to predict optimal scheduling patterns
    """
    
    def __init__(self):
        # User behavior patterns (learned from historical data)
        self.user_patterns = {}
        
        # Task completion predictions
        self.completion_predictions = {}
        
        # Feature weights for scoring algorithm
        self.feature_weights = {
            'time_of_day': 0.25,
            'day_of_week': 0.20,
            'task_type': 0.15,
            'historical_success': 0.20,
            'workload_balance': 0.10,
            'deadline_proximity': 0.10
        }
    
    async def train_on_user_data(
        self,
        user_id: str,
        historical_tasks: List[Dict],
        historical_events: List[Dict]
    ):
        """
        Train model on user's historical data
        
        Args:
            historical_tasks: Completed tasks with timestamps
            historical_events: Past events/meetings
        """
        
        # Extract patterns
        completion_patterns = self._extract_completion_patterns(historical_tasks)
        scheduling_preferences = self._extract_scheduling_preferences(historical_events)
        productivity_patterns = self._extract_productivity_patterns(historical_tasks)
        
        # Store learned patterns
        self.user_patterns[user_id] = {
            'completion': completion_patterns,
            'scheduling': scheduling_preferences,
            'productivity': productivity_patterns,
            'last_updated': datetime.now().isoformat()
        }
    
    def predict_completion_time(
        self,
        task: Dict,
        user_id: str
    ) -> Tuple[int, float]:
        """
        Predict how long a task will actually take
        
        Args:
            task: Task with estimated_duration
            user_id: User ID
        
        Returns:
            (predicted_minutes, confidence)
        """
        
        estimated = task.get('estimated_duration', 60)
        
        # If no historical data, return estimate
        if user_id not in self.user_patterns:
            return estimated, 0.5
        
        patterns = self.user_patterns[user_id]['completion']
        
        # Adjust based on historical accuracy
        task_type = self._categorize_task_type(task['title'])
        
        if task_type in patterns['type_duration_ratios']:
            ratio = patterns['type_duration_ratios'][task_type]
            predicted = int(estimated * ratio)
            confidence = patterns['type_confidence'].get(task_type, 0.5)
            return predicted, confidence
        
        # Use overall average ratio
        avg_ratio = patterns.get('overall_duration_ratio', 1.0)
        return int(estimated * avg_ratio), 0.6
    
    def predict_best_schedule_day(
        self,
        task: Dict,
        user_id: str,
        available_days: List[datetime]
    ) -> List[Tuple[datetime, float]]:
        """
        Predict best days to schedule a task
        
        Returns:
            List of (day, score) tuples sorted by score
        """
        
        if user_id not in self.user_patterns:
            # Default: score all days equally
            return [(day, 0.5) for day in available_days]
        
        patterns = self.user_patterns[user_id]
        scored_days = []
        
        for day in available_days:
            score = self._calculate_day_score(task, day, patterns)
            scored_days.append((day, score))
        
        return sorted(scored_days, key=lambda x: x[1], reverse=True)
    
    def calculate_scheduling_score(
        self,
        task: Dict,
        proposed_time: datetime,
        user_id: str,
        current_schedule: List[Dict]
    ) -> float:
        """
        Calculate a score (0-100) for scheduling a task at proposed time
        
        Considers:
        - Historical patterns
        - Time of day
        - Day of week
        - Current workload
        - Deadline proximity
        """
        
        scores = {}
        
        # Time of day score
        scores['time_of_day'] = self._score_time_of_day(
            proposed_time.hour,
            user_id
        )
        
        # Day of week score
        scores['day_of_week'] = self._score_day_of_week(
            proposed_time.weekday(),
            user_id
        )
        
        # Task type alignment
        task_type = self._categorize_task_type(task['title'])
        scores['task_type'] = self._score_task_type_alignment(
            task_type,
            proposed_time.hour
        )
        
        # Historical success rate at this time
        scores['historical_success'] = self._score_historical_success(
            proposed_time,
            user_id
        )
        
        # Workload balance
        scores['workload_balance'] = self._score_workload_balance(
            proposed_time,
            current_schedule
        )
        
        # Deadline proximity
        if task.get('due_date'):
            scores['deadline_proximity'] = self._score_deadline_proximity(
                proposed_time,
                task['due_date']
            )
        else:
            scores['deadline_proximity'] = 50  # Neutral
        
        # Calculate weighted total
        total_score = sum(
            scores[feature] * self.feature_weights[feature]
            for feature in scores
        )
        
        return min(100, max(0, total_score))
    
    def detect_scheduling_patterns(
        self,
        tasks: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        Detect patterns in user's scheduling behavior
        
        Returns:
            {
                'preferred_days': [1, 2, 3],  # Mon, Tue, Wed
                'preferred_hours': [10, 11, 14],
                'task_clustering': {
                    'meetings': 'afternoon',
                    'deep_work': 'morning'
                },
                'avg_daily_tasks': 5,
                'avg_task_duration': 45
            }
        """
        
        # Analyze day preferences
        day_counts = Counter([
            t.get('completed_at', t.get('due_date')).weekday()
            for t in tasks
            if t.get('completed_at') or t.get('due_date')
        ])
        preferred_days = [day for day, _ in day_counts.most_common(3)]
        
        # Analyze hour preferences
        hour_counts = Counter([
            t.get('completed_at', t.get('created_at')).hour
            for t in tasks
            if t.get('completed_at') or t.get('created_at')
        ])
        preferred_hours = [hour for hour, _ in hour_counts.most_common(5)]
        
        # Task clustering
        task_clustering = self._cluster_tasks_by_time(tasks)
        
        # Average metrics
        avg_daily_tasks = len(tasks) / max(90, 1)  # Assume 90 days of data
        durations = [t.get('estimated_duration', 60) for t in tasks]
        avg_task_duration = np.mean(durations) if durations else 60
        
        return {
            'preferred_days': preferred_days,
            'preferred_hours': preferred_hours,
            'task_clustering': task_clustering,
            'avg_daily_tasks': round(avg_daily_tasks, 1),
            'avg_task_duration': round(avg_task_duration)
        }
    
    def predict_task_conflicts(
        self,
        new_task: Dict,
        existing_schedule: List[Dict]
    ) -> List[Dict]:
        """
        Predict potential conflicts before scheduling
        
        Returns list of potential conflicts with severity scores
        """
        
        conflicts = []
        
        if not new_task.get('due_date'):
            return conflicts
        
        task_duration = new_task.get('estimated_duration', 60)
        task_end = new_task['due_date'] + timedelta(minutes=task_duration)
        
        for item in existing_schedule:
            # Check time overlap
            if 'start_time' in item and 'end_time' in item:
                if self._times_overlap(
                    new_task['due_date'], task_end,
                    item['start_time'], item['end_time']
                ):
                    conflicts.append({
                        'type': 'time_overlap',
                        'item': item,
                        'severity': self._calculate_conflict_severity(
                            new_task, item
                        )
                    })
        
        return sorted(conflicts, key=lambda x: x['severity'], reverse=True)
    
    # ==================== Private Methods ====================
    
    def _extract_completion_patterns(self, tasks: List[Dict]) -> Dict:
        """Extract task completion patterns"""
        
        type_durations = defaultdict(list)
        type_estimates = defaultdict(list)
        
        for task in tasks:
            if task.get('status') != 'COMPLETED':
                continue
            
            task_type = self._categorize_task_type(task['title'])
            
            # Actual duration (if available)
            if task.get('completed_at') and task.get('started_at'):
                actual = (task['completed_at'] - task['started_at']).total_seconds() / 60
                estimated = task.get('estimated_duration', 60)
                
                type_durations[task_type].append(actual)
                type_estimates[task_type].append(estimated)
        
        # Calculate ratios (actual/estimated)
        type_duration_ratios = {}
        type_confidence = {}
        
        for task_type in type_durations:
            if type_estimates[task_type]:
                ratios = [
                    actual / estimated
                    for actual, estimated in zip(type_durations[task_type], type_estimates[task_type])
                    if estimated > 0
                ]
                
                if ratios:
                    type_duration_ratios[task_type] = np.mean(ratios)
                    type_confidence[task_type] = 1.0 - min(0.5, np.std(ratios))
        
        # Overall ratio
        all_ratios = list(type_duration_ratios.values())
        overall_ratio = np.mean(all_ratios) if all_ratios else 1.0
        
        return {
            'type_duration_ratios': type_duration_ratios,
            'type_confidence': type_confidence,
            'overall_duration_ratio': overall_ratio
        }
    
    def _extract_scheduling_preferences(self, events: List[Dict]) -> Dict:
        """Extract scheduling preferences from events"""
        
        hour_frequencies = defaultdict(int)
        day_frequencies = defaultdict(int)
        
        for event in events:
            if 'start_time' in event:
                hour_frequencies[event['start_time'].hour] += 1
                day_frequencies[event['start_time'].weekday()] += 1
        
        return {
            'preferred_hours': sorted(
                hour_frequencies.keys(),
                key=hour_frequencies.get,
                reverse=True
            )[:5],
            'preferred_days': sorted(
                day_frequencies.keys(),
                key=day_frequencies.get,
                reverse=True
            )[:3]
        }
    
    def _extract_productivity_patterns(self, tasks: List[Dict]) -> Dict:
        """Extract productivity patterns"""
        
        hourly_completions = defaultdict(int)
        daily_completions = defaultdict(int)
        
        for task in tasks:
            if task.get('status') == 'COMPLETED' and task.get('completed_at'):
                hour = task['completed_at'].hour
                day = task['completed_at'].weekday()
                
                hourly_completions[hour] += 1
                daily_completions[day] += 1
        
        return {
            'peak_hours': sorted(
                hourly_completions.keys(),
                key=hourly_completions.get,
                reverse=True
            )[:5],
            'peak_days': sorted(
                daily_completions.keys(),
                key=daily_completions.get,
                reverse=True
            )[:3],
            'hourly_distribution': dict(hourly_completions),
            'daily_distribution': dict(daily_completions)
        }
    
    def _categorize_task_type(self, title: str) -> str:
        """Categorize task based on title keywords"""
        
        title_lower = title.lower()
        
        keywords = {
            'meeting': ['meeting', 'call', 'conference', 'discussion'],
            'coding': ['code', 'develop', 'debug', 'implement', 'fix'],
            'writing': ['write', 'document', 'report', 'article', 'email'],
            'review': ['review', 'check', 'audit', 'analyze'],
            'planning': ['plan', 'schedule', 'organize', 'prepare'],
            'admin': ['admin', 'paperwork', 'file', 'form']
        }
        
        for task_type, words in keywords.items():
            if any(word in title_lower for word in words):
                return task_type
        
        return 'general'
    
    def _calculate_day_score(
        self,
        task: Dict,
        day: datetime,
        patterns: Dict
    ) -> float:
        """Calculate score for scheduling on a specific day"""
        
        score = 50  # Base score
        
        # Check if day is in preferred days
        if 'productivity' in patterns:
            if day.weekday() in patterns['productivity']['peak_days']:
                score += 20
        
        # Check deadline proximity
        if task.get('due_date'):
            days_until_due = (task['due_date'] - day).days
            if 0 <= days_until_due <= 2:
                score += 15  # Bonus for scheduling near deadline
            elif days_until_due < 0:
                score -= 30  # Penalty for past deadline
        
        # Weekend penalty (unless user prefers)
        if day.weekday() >= 5:  # Sat/Sun
            score -= 10
        
        return max(0, min(100, score))
    
    def _score_time_of_day(self, hour: int, user_id: str) -> float:
        """Score based on time of day (0-100)"""
        
        if user_id not in self.user_patterns:
            # Default: prefer 9-5
            if 9 <= hour <= 17:
                return 80
            return 40
        
        productivity = self.user_patterns[user_id].get('productivity', {})
        peak_hours = productivity.get('peak_hours', [])
        
        if hour in peak_hours:
            return 90
        elif 9 <= hour <= 17:
            return 60
        else:
            return 30
    
    def _score_day_of_week(self, weekday: int, user_id: str) -> float:
        """Score based on day of week (0-100)"""
        
        if user_id not in self.user_patterns:
            # Default: prefer mid-week
            if weekday in [1, 2, 3]:  # Tue, Wed, Thu
                return 80
            return 60
        
        productivity = self.user_patterns[user_id].get('productivity', {})
        peak_days = productivity.get('peak_days', [])
        
        if weekday in peak_days:
            return 90
        elif weekday < 5:  # Weekday
            return 60
        else:  # Weekend
            return 40
    
    def _score_task_type_alignment(self, task_type: str, hour: int) -> float:
        """Score task type alignment with time of day"""
        
        optimal_times = {
            'meeting': [10, 11, 14, 15, 16],
            'coding': [9, 10, 11, 14, 15],
            'writing': [9, 10, 11, 15],
            'review': [16, 17],
            'planning': [8, 9, 17],
            'admin': [8, 13, 17]
        }
        
        if task_type in optimal_times:
            if hour in optimal_times[task_type]:
                return 90
        
        return 60
    
    def _score_historical_success(self, proposed_time: datetime, user_id: str) -> float:
        """Score based on historical success at this time"""
        
        if user_id not in self.user_patterns:
            return 60
        
        productivity = self.user_patterns[user_id].get('productivity', {})
        hourly_dist = productivity.get('hourly_distribution', {})
        
        completions = hourly_dist.get(proposed_time.hour, 0)
        max_completions = max(hourly_dist.values()) if hourly_dist else 1
        
        if max_completions == 0:
            return 60
        
        return 50 + (completions / max_completions) * 50
    
    def _score_workload_balance(
        self,
        proposed_time: datetime,
        current_schedule: List[Dict]
    ) -> float:
        """Score based on workload balance"""
        
        # Count items on same day
        same_day_count = sum(
            1 for item in current_schedule
            if 'start_time' in item and item['start_time'].date() == proposed_time.date()
        )
        
        if same_day_count == 0:
            return 100
        elif same_day_count <= 3:
            return 80
        elif same_day_count <= 6:
            return 60
        else:
            return 40
    
    def _score_deadline_proximity(
        self,
        proposed_time: datetime,
        deadline: datetime
    ) -> float:
        """Score based on proximity to deadline"""
        
        days_before_deadline = (deadline - proposed_time).days
        
        if days_before_deadline < 0:
            return 0  # Past deadline
        elif days_before_deadline == 0:
            return 100  # Same day as deadline
        elif days_before_deadline <= 2:
            return 90  # Close to deadline
        elif days_before_deadline <= 7:
            return 70  # Within a week
        else:
            return 60  # Plenty of time
    
    def _cluster_tasks_by_time(self, tasks: List[Dict]) -> Dict:
        """Cluster tasks by time of day"""
        
        morning_tasks = defaultdict(int)  # 6-12
        afternoon_tasks = defaultdict(int)  # 12-17
        evening_tasks = defaultdict(int)  # 17-22
        
        for task in tasks:
            task_type = self._categorize_task_type(task['title'])
            
            if task.get('completed_at'):
                hour = task['completed_at'].hour
                if 6 <= hour < 12:
                    morning_tasks[task_type] += 1
                elif 12 <= hour < 17:
                    afternoon_tasks[task_type] += 1
                elif 17 <= hour < 22:
                    evening_tasks[task_type] += 1
        
        clustering = {}
        for task_type in set(list(morning_tasks.keys()) + list(afternoon_tasks.keys()) + list(evening_tasks.keys())):
            counts = {
                'morning': morning_tasks[task_type],
                'afternoon': afternoon_tasks[task_type],
                'evening': evening_tasks[task_type]
            }
            clustering[task_type] = max(counts, key=counts.get)
        
        return clustering
    
    def _calculate_conflict_severity(self, task: Dict, conflicting_item: Dict) -> float:
        """Calculate severity of conflict (0-100)"""
        
        severity = 50  # Base
        
        # Higher priority = higher severity
        if task.get('priority') == 'HIGH':
            severity += 30
        
        # Closer deadline = higher severity
        if task.get('due_date'):
            days_until = (task['due_date'] - datetime.now()).days
            if days_until <= 1:
                severity += 20
        
        return min(100, severity)
    
    @staticmethod
    def _times_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and end1 > start2
