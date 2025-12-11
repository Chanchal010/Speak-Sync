"""
Smart Scheduling Service - AI-powered task and event scheduling
Provides intelligent suggestions, conflict detection, and time optimization
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import asyncio
from collections import defaultdict
import statistics

from .nlu_service import NLUService


class SchedulingService:
    """
    Intelligent scheduling assistant with ML-based optimization
    """
    
    def __init__(self, nlu_service: Optional[NLUService] = None, db_pool=None):
        self.db = db_pool  # Will be injected from main app
        self.nlu_service = nlu_service
        
        # Priority weights for scheduling algorithm
        self.priority_weights = {
            'URGENT_IMPORTANT': 10,    # Eisenhower: Do First
            'NOT_URGENT_IMPORTANT': 7,  # Eisenhower: Schedule
            'URGENT_NOT_IMPORTANT': 4,  # Eisenhower: Delegate
            'NOT_URGENT_NOT_IMPORTANT': 1  # Eisenhower: Eliminate
        }
        
        # Time slot preferences (hours of day)
        self.optimal_time_slots = {
            'deep_work': [9, 10, 11, 14, 15],  # Focus hours
            'meetings': [10, 11, 14, 15, 16],   # Meeting hours
            'routine': [8, 9, 17, 18],          # Routine tasks
            'review': [16, 17]                  # End of day
        }
    
    async def initialize(self, db_pool):
        """Initialize database connection"""
        self.db = db_pool
    
    async def analyze_schedule_conflicts(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Detect conflicts and overlapping commitments
        
        Returns:
            {
                'conflicts': [
                    {
                        'type': 'overlap',
                        'items': [event1, event2],
                        'severity': 'high',
                        'suggestion': 'Reschedule event1 to 3pm'
                    }
                ],
                'overloaded_days': [
                    {
                        'date': '2025-12-15',
                        'load': 12,  # hours
                        'recommendation': 'Move 2 tasks to Dec 16'
                    }
                ],
                'gaps': [
                    {
                        'date': '2025-12-14',
                        'start': '10:00',
                        'end': '12:00',
                        'duration': 120,  # minutes
                        'suggestion': 'Schedule deep work here'
                    }
                ]
            }
        """
        
        # Get all scheduled items
        events = await self._get_events(user_id, start_date, end_date)
        tasks = await self._get_tasks(user_id, start_date, end_date)
        
        # Detect conflicts
        conflicts = self._detect_conflicts(events, tasks)
        
        # Detect overloaded days
        overloaded_days = self._detect_overloaded_days(events, tasks)
        
        # Find available gaps
        gaps = self._find_time_gaps(events, tasks, start_date, end_date)
        
        return {
            'conflicts': conflicts,
            'overloaded_days': overloaded_days,
            'gaps': gaps,
            'summary': {
                'total_conflicts': len(conflicts),
                'high_severity': len([c for c in conflicts if c['severity'] == 'high']),
                'total_overloaded_days': len(overloaded_days),
                'total_available_gaps': len(gaps)
            }
        }
    
    async def suggest_optimal_time_slot(
        self,
        user_id: str,
        task_type: str,
        duration_minutes: int,
        deadline: Optional[datetime] = None,
        preferred_days: Optional[List[int]] = None
    ) -> List[Dict]:
        """
        Suggest best time slots for a task based on:
        - User's historical patterns
        - Current schedule
        - Task type and priority
        - Available energy levels (time of day)
        
        Args:
            task_type: 'deep_work', 'meeting', 'routine', 'review'
            duration_minutes: Task duration
            deadline: Latest completion time
            preferred_days: List of weekday numbers (0=Monday)
        
        Returns:
            List of suggested time slots ranked by score
        """
        
        # Get user's schedule for next 14 days
        end_date = datetime.now() + timedelta(days=14)
        if deadline and deadline < end_date:
            end_date = deadline
        
        events = await self._get_events(user_id, datetime.now(), end_date)
        tasks = await self._get_tasks(user_id, datetime.now(), end_date)
        
        # Analyze user patterns
        patterns = await self._analyze_user_time_patterns(user_id)
        
        # Generate candidate slots
        candidates = self._generate_candidate_slots(
            events, tasks, 
            datetime.now(), end_date,
            duration_minutes
        )
        
        # Score each slot
        scored_slots = []
        for slot in candidates:
            score = self._calculate_slot_score(
                slot, task_type, patterns, preferred_days
            )
            scored_slots.append({
                **slot,
                'score': score,
                'confidence': score / 100,  # Normalize to 0-1
                'reason': self._explain_slot_score(slot, task_type, score)
            })
        
        # Return top 5 suggestions
        return sorted(scored_slots, key=lambda x: x['score'], reverse=True)[:5]
    
    async def optimize_task_schedule(
        self,
        user_id: str,
        task_ids: List[str]
    ) -> Dict:
        """
        Re-arrange multiple tasks optimally
        
        Returns:
            {
                'optimized_schedule': [
                    {
                        'task_id': '123',
                        'suggested_time': '2025-12-15T10:00:00Z',
                        'reason': 'Optimal focus time, no conflicts'
                    }
                ],
                'improvements': {
                    'conflicts_resolved': 3,
                    'workload_balanced': True,
                    'estimated_time_saved': 120  # minutes
                }
            }
        """
        
        # Get tasks details
        tasks = []
        for task_id in task_ids:
            task = await self._get_task_by_id(user_id, task_id)
            if task:
                tasks.append(task)
        
        # Get existing schedule
        end_date = datetime.now() + timedelta(days=14)
        events = await self._get_events(user_id, datetime.now(), end_date)
        
        # Apply scheduling algorithm
        optimized = self._apply_scheduling_algorithm(
            tasks, events, datetime.now(), end_date
        )
        
        # Calculate improvements
        original_conflicts = len(self._detect_conflicts(events, tasks))
        new_conflicts = len(self._detect_conflicts(events, optimized))
        
        return {
            'optimized_schedule': optimized,
            'improvements': {
                'conflicts_resolved': max(0, original_conflicts - new_conflicts),
                'workload_balanced': self._is_workload_balanced(optimized),
                'estimated_time_saved': self._calculate_time_savings(tasks, optimized)
            }
        }
    
    async def get_smart_suggestions(
        self,
        user_id: str,
        context: Optional[Dict] = None
    ) -> List[str]:
        """
        Generate proactive scheduling suggestions
        
        Context: {
            'current_time': datetime,
            'last_activity': datetime,
            'location': 'home|work|gym'
        }
        
        Returns:
            [
                "You have 3 urgent tasks due tomorrow. Want to schedule them?",
                "Friday evening - good time to review next week's tasks",
                "Your calendar is light next Tuesday. Good day for deep work?"
            ]
        """
        
        suggestions = []
        current_time = context.get('current_time', datetime.now()) if context else datetime.now()
        
        # Check for urgent tasks
        urgent_tasks = await self._get_urgent_tasks(user_id)
        if len(urgent_tasks) >= 3:
            suggestions.append(
                f"You have {len(urgent_tasks)} urgent tasks due soon. "
                "Want me to help schedule them?"
            )
        
        # Friday evening - weekly review
        if current_time.weekday() == 4 and current_time.hour >= 17:
            suggestions.append(
                "It's Friday evening. Good time to review and plan next week's tasks?"
            )
        
        # Check for free days
        free_days = await self._find_free_days(user_id, 7)
        if free_days:
            day_name = free_days[0].strftime('%A')
            suggestions.append(
                f"Your calendar is light next {day_name}. "
                "Great day for deep work or important tasks."
            )
        
        # Overloaded day warning
        overloaded = await self._check_overloaded_days(user_id, 3)
        if overloaded:
            date_str = overloaded[0].strftime('%b %d')
            suggestions.append(
                f"{date_str} looks packed. Want to reschedule some tasks?"
            )
        
        return suggestions[:3]  # Top 3 suggestions
    
    # ==================== Private Helper Methods ====================
    
    async def _get_events(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """Fetch events from database"""
        query = """
        SELECT id, title, start_time, end_time, location, all_day
        FROM events
        WHERE user_id = $1 
          AND start_time >= $2 
          AND start_time <= $3
          AND deleted_at IS NULL
        ORDER BY start_time
        """
        rows = await self.db.fetch(query, user_id, start_date, end_date)
        return [dict(row) for row in rows]
    
    async def _get_tasks(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Fetch tasks with due dates"""
        query = """
        SELECT id, title, due_date, estimated_duration, 
               priority, eisenhower_category, status
        FROM tasks
        WHERE user_id = $1 
          AND due_date >= $2 
          AND due_date <= $3
          AND status != 'COMPLETED'
          AND deleted_at IS NULL
        ORDER BY due_date, priority DESC
        """
        rows = await self.db.fetch(query, user_id, start_date, end_date)
        return [dict(row) for row in rows]
    
    async def _get_task_by_id(self, user_id: str, task_id: str) -> Optional[Dict]:
        """Fetch single task"""
        query = """
        SELECT id, title, due_date, estimated_duration,
               priority, eisenhower_category, status
        FROM tasks
        WHERE id = $1 AND user_id = $2 AND deleted_at IS NULL
        """
        row = await self.db.fetchrow(query, task_id, user_id)
        return dict(row) if row else None
    
    def _detect_conflicts(
        self, 
        events: List[Dict], 
        tasks: List[Dict]
    ) -> List[Dict]:
        """Detect scheduling conflicts"""
        conflicts = []
        
        # Check event overlaps
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if self._times_overlap(
                    event1['start_time'], event1['end_time'],
                    event2['start_time'], event2['end_time']
                ):
                    conflicts.append({
                        'type': 'event_overlap',
                        'items': [event1, event2],
                        'severity': 'high',
                        'suggestion': f"Reschedule '{event2['title']}' to avoid conflict"
                    })
        
        # Check tasks vs events conflicts
        for task in tasks:
            if not task.get('due_date'):
                continue
            
            for event in events:
                # If task is due during an event
                if (task['due_date'] >= event['start_time'] and 
                    task['due_date'] <= event['end_time']):
                    conflicts.append({
                        'type': 'task_event_conflict',
                        'items': [task, event],
                        'severity': 'medium',
                        'suggestion': f"Task '{task['title']}' due during '{event['title']}'"
                    })
        
        return conflicts
    
    def _detect_overloaded_days(
        self,
        events: List[Dict],
        tasks: List[Dict]
    ) -> List[Dict]:
        """Find days with too many commitments"""
        day_loads = defaultdict(float)
        
        # Calculate load per day
        for event in events:
            if event.get('all_day'):
                continue
            date = event['start_time'].date()
            duration = (event['end_time'] - event['start_time']).total_seconds() / 3600
            day_loads[date] += duration
        
        for task in tasks:
            if task.get('estimated_duration') and task.get('due_date'):
                date = task['due_date'].date()
                day_loads[date] += task['estimated_duration'] / 60  # Convert minutes to hours
        
        # Flag days > 10 hours
        overloaded = []
        for date, load in day_loads.items():
            if load > 10:
                overloaded.append({
                    'date': date.isoformat(),
                    'load': round(load, 1),
                    'recommendation': f'Move some tasks from {date.strftime("%b %d")} to lighter days'
                })
        
        return sorted(overloaded, key=lambda x: x['load'], reverse=True)
    
    def _find_time_gaps(
        self,
        events: List[Dict],
        tasks: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Find available time gaps for scheduling"""
        gaps = []
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            # Working hours: 9am - 6pm
            day_start = datetime.combine(current_date, datetime.min.time().replace(hour=9))
            day_end = datetime.combine(current_date, datetime.min.time().replace(hour=18))
            
            # Get all items for this day
            day_events = [
                e for e in events 
                if e['start_time'].date() == current_date
            ]
            
            # Sort by start time
            day_events.sort(key=lambda x: x['start_time'])
            
            # Find gaps between events
            current_time = day_start
            for event in day_events:
                gap_duration = (event['start_time'] - current_time).total_seconds() / 60
                
                if gap_duration >= 30:  # At least 30 min gap
                    gaps.append({
                        'date': current_date.isoformat(),
                        'start': current_time.strftime('%H:%M'),
                        'end': event['start_time'].strftime('%H:%M'),
                        'duration': int(gap_duration),
                        'suggestion': self._suggest_task_for_gap(gap_duration)
                    })
                
                current_time = event['end_time']
            
            # Gap after last event
            if current_time < day_end:
                gap_duration = (day_end - current_time).total_seconds() / 60
                if gap_duration >= 30:
                    gaps.append({
                        'date': current_date.isoformat(),
                        'start': current_time.strftime('%H:%M'),
                        'end': day_end.strftime('%H:%M'),
                        'duration': int(gap_duration),
                        'suggestion': self._suggest_task_for_gap(gap_duration)
                    })
            
            current_date += timedelta(days=1)
        
        return gaps
    
    def _suggest_task_for_gap(self, duration_minutes: float) -> str:
        """Suggest task type based on available time"""
        if duration_minutes >= 120:
            return "Schedule deep work or focus time"
        elif duration_minutes >= 60:
            return "Good for meetings or moderate tasks"
        else:
            return "Perfect for quick tasks or emails"
    
    async def _analyze_user_time_patterns(self, user_id: str) -> Dict:
        """Learn when user is most productive"""
        query = """
        SELECT 
            EXTRACT(HOUR FROM completed_at) as hour,
            EXTRACT(DOW FROM completed_at) as day_of_week,
            COUNT(*) as completed_count
        FROM tasks
        WHERE user_id = $1
          AND status = 'COMPLETED'
          AND completed_at > NOW() - INTERVAL '90 days'
        GROUP BY hour, day_of_week
        """
        rows = await self.db.fetch(query, user_id)
        
        if not rows:
            # Default patterns if no data
            return {
                'peak_hours': [10, 11, 14, 15],
                'peak_days': [1, 2, 3],  # Tue, Wed, Thu
                'completion_rate_by_hour': {}
            }
        
        # Find peak productivity times
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for row in rows:
            hour_counts[int(row['hour'])] += row['completed_count']
            day_counts[int(row['day_of_week'])] += row['completed_count']
        
        # Top 5 hours and days
        peak_hours = sorted(hour_counts.keys(), key=hour_counts.get, reverse=True)[:5]
        peak_days = sorted(day_counts.keys(), key=day_counts.get, reverse=True)[:3]
        
        return {
            'peak_hours': peak_hours,
            'peak_days': peak_days,
            'completion_rate_by_hour': dict(hour_counts)
        }
    
    def _generate_candidate_slots(
        self,
        events: List[Dict],
        tasks: List[Dict],
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int
    ) -> List[Dict]:
        """Generate possible time slots"""
        slots = []
        current_date = start_date.date()
        
        while current_date <= end_date.date():
            # Check each hour from 9am to 6pm
            for hour in range(9, 18):
                slot_start = datetime.combine(
                    current_date, 
                    datetime.min.time().replace(hour=hour)
                )
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                
                # Check if slot is available
                has_conflict = False
                for event in events:
                    if self._times_overlap(
                        slot_start, slot_end,
                        event['start_time'], event['end_time']
                    ):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    slots.append({
                        'start': slot_start,
                        'end': slot_end,
                        'date': current_date.isoformat(),
                        'hour': hour,
                        'day_of_week': current_date.weekday()
                    })
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _calculate_slot_score(
        self,
        slot: Dict,
        task_type: str,
        patterns: Dict,
        preferred_days: Optional[List[int]]
    ) -> float:
        """Score a time slot (0-100)"""
        score = 50  # Base score
        
        # Bonus for peak productivity hours
        if slot['hour'] in patterns['peak_hours']:
            score += 20
        
        # Bonus for peak days
        if slot['day_of_week'] in patterns['peak_days']:
            score += 15
        
        # Bonus for optimal time slots by task type
        if task_type in self.optimal_time_slots:
            if slot['hour'] in self.optimal_time_slots[task_type]:
                score += 15
        
        # Bonus for user's preferred days
        if preferred_days and slot['day_of_week'] in preferred_days:
            score += 10
        
        # Penalty for early morning or late evening
        if slot['hour'] < 9 or slot['hour'] > 17:
            score -= 20
        
        return max(0, min(100, score))
    
    def _explain_slot_score(
        self,
        slot: Dict,
        task_type: str,
        score: float
    ) -> str:
        """Explain why this slot was suggested"""
        reasons = []
        
        if score >= 80:
            reasons.append("Optimal time based on your patterns")
        elif score >= 60:
            reasons.append("Good time with no conflicts")
        else:
            reasons.append("Available slot")
        
        if task_type == 'deep_work' and slot['hour'] in [10, 11, 14, 15]:
            reasons.append("Peak focus hours")
        
        return ". ".join(reasons)
    
    def _apply_scheduling_algorithm(
        self,
        tasks: List[Dict],
        events: List[Dict],
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Apply priority-based scheduling algorithm"""
        optimized = []
        
        # Sort tasks by priority and deadline
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                -self.priority_weights.get(t.get('eisenhower_category', 'NOT_URGENT_NOT_IMPORTANT'), 1),
                t.get('due_date', end_date)
            )
        )
        
        # Schedule each task
        for task in sorted_tasks:
            duration = task.get('estimated_duration', 60)  # Default 60 min
            
            # Find best slot
            slots = self._generate_candidate_slots(
                events, [], start_date, end_date, duration
            )
            
            if slots:
                best_slot = slots[0]  # First available
                optimized.append({
                    'task_id': task['id'],
                    'suggested_time': best_slot['start'].isoformat(),
                    'reason': 'Optimal time based on priority and availability'
                })
                
                # Add to events to prevent future conflicts
                events.append({
                    'start_time': best_slot['start'],
                    'end_time': best_slot['end'],
                    'title': task['title']
                })
        
        return optimized
    
    def _is_workload_balanced(self, schedule: List[Dict]) -> bool:
        """Check if workload is evenly distributed"""
        day_loads = defaultdict(int)
        
        for item in schedule:
            date = datetime.fromisoformat(item['suggested_time']).date()
            day_loads[date] += 1
        
        if not day_loads:
            return True
        
        loads = list(day_loads.values())
        std_dev = statistics.stdev(loads) if len(loads) > 1 else 0
        
        return std_dev < 2  # Low standard deviation = balanced
    
    def _calculate_time_savings(
        self,
        original: List[Dict],
        optimized: List[Dict]
    ) -> int:
        """Estimate time saved by optimization (minutes)"""
        # Placeholder calculation
        return len(optimized) * 15  # Assume 15 min saved per task
    
    async def _get_urgent_tasks(self, user_id: str) -> List[Dict]:
        """Get tasks due in next 48 hours"""
        query = """
        SELECT id, title, due_date, priority
        FROM tasks
        WHERE user_id = $1
          AND status != 'COMPLETED'
          AND due_date <= NOW() + INTERVAL '48 hours'
          AND deleted_at IS NULL
        ORDER BY due_date
        """
        rows = await self.db.fetch(query, user_id)
        return [dict(row) for row in rows]
    
    async def _find_free_days(self, user_id: str, days_ahead: int) -> List[datetime]:
        """Find days with light schedules"""
        end_date = datetime.now() + timedelta(days=days_ahead)
        events = await self._get_events(user_id, datetime.now(), end_date)
        
        # Count events per day
        day_counts = defaultdict(int)
        for event in events:
            day_counts[event['start_time'].date()] += 1
        
        # Find days with <= 2 events
        free_days = []
        for i in range(days_ahead):
            date = (datetime.now() + timedelta(days=i)).date()
            if day_counts[date] <= 2:
                free_days.append(datetime.combine(date, datetime.min.time()))
        
        return free_days
    
    async def _check_overloaded_days(
        self,
        user_id: str,
        days_ahead: int
    ) -> List[datetime]:
        """Find overloaded days in next N days"""
        end_date = datetime.now() + timedelta(days=days_ahead)
        events = await self._get_events(user_id, datetime.now(), end_date)
        tasks = await self._get_tasks(user_id, datetime.now(), end_date)
        
        overloaded = self._detect_overloaded_days(events, tasks)
        
        return [
            datetime.fromisoformat(day['date'])
            for day in overloaded
        ]
    
    @staticmethod
    def _times_overlap(
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time ranges overlap"""
        return start1 < end2 and end1 > start2
