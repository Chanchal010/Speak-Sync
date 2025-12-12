"""
ML Model for Habit Formation and Prediction
Uses behavioral science and machine learning for habit analysis
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from collections import defaultdict, Counter
import statistics


class HabitFormationModel:
    """
    Machine Learning model for habit formation prediction
    Based on behavioral psychology and habit formation research
    """
    
    def __init__(self):
        # Habit formation parameters (based on research)
        self.FORMATION_THRESHOLD = 66  # Average days to form habit (Lally et al., 2010)
        self.CRITICAL_PERIOD = 21  # First 21 days are most critical
        self.AUTOMATICITY_CURVE = 0.015  # Daily increase in automaticity
        
        # Behavior change stages (Prochaska & DiClemente)
        self.stages = {
            'precontemplation': 0,
            'contemplation': 1,
            'preparation': 2,
            'action': 3,
            'maintenance': 4,
            'termination': 5
        }
        
        # Feature weights for habit strength
        self.feature_weights = {
            'consistency': 0.30,
            'frequency': 0.25,
            'duration': 0.15,
            'timing_stability': 0.15,
            'context_stability': 0.15
        }
    
    def calculate_habit_strength(
        self,
        logs: List[Dict],
        days_tracked: int
    ) -> float:
        """
        Calculate overall habit strength (0-100)
        
        Based on:
        - Consistency of performance
        - Frequency relative to goal
        - Duration of engagement
        - Temporal stability
        - Contextual cues
        """
        
        if not logs or days_tracked == 0:
            return 0.0
        
        scores = {}
        
        # 1. Consistency Score
        logged_days = len(set(log['date'].split('T')[0] for log in logs))
        consistency = logged_days / days_tracked
        scores['consistency'] = consistency * 100
        
        # 2. Frequency Score (compared to ideal)
        actual_frequency = len(logs) / (days_tracked / 7)  # per week
        ideal_frequency = 7  # daily
        frequency = min(1.0, actual_frequency / ideal_frequency)
        scores['frequency'] = frequency * 100
        
        # 3. Duration Score (engagement time)
        durations = [log.get('duration', 0) for log in logs if log.get('duration')]
        if durations:
            avg_duration = statistics.mean(durations)
            # Normalize to 30 min baseline
            duration_score = min(1.0, avg_duration / 30)
            scores['duration'] = duration_score * 100
        else:
            scores['duration'] = 50  # Neutral if no duration data
        
        # 4. Timing Stability Score
        hours = [datetime.fromisoformat(log['date'].replace('Z', '')).hour for log in logs]
        if len(hours) > 1:
            hour_variance = statistics.variance(hours)
            # Lower variance = higher stability
            timing_stability = 1 / (1 + hour_variance / 4)
            scores['timing_stability'] = timing_stability * 100
        else:
            scores['timing_stability'] = 50
        
        # 5. Context Stability Score
        # If habit is done in same context/location
        contexts = [log.get('context', 'default') for log in logs]
        if contexts:
            most_common_context = Counter(contexts).most_common(1)[0][1]
            context_stability = most_common_context / len(contexts)
            scores['context_stability'] = context_stability * 100
        else:
            scores['context_stability'] = 50
        
        # Calculate weighted total
        total_strength = sum(
            scores[feature] * self.feature_weights[feature]
            for feature in scores
        )
        
        return min(100, max(0, total_strength))
    
    def predict_automaticity(
        self,
        current_streak: int,
        habit_strength: float
    ) -> float:
        """
        Predict how automatic the habit feels (0-1)
        
        Based on research: automaticity increases logarithmically
        """
        
        # Base automaticity from streak length
        if current_streak < self.FORMATION_THRESHOLD:
            base_automaticity = (current_streak / self.FORMATION_THRESHOLD) ** 0.7
        else:
            base_automaticity = 0.95  # Near complete automation
        
        # Adjust based on habit strength
        strength_factor = habit_strength / 100
        automaticity = base_automaticity * strength_factor
        
        return min(1.0, automaticity)
    
    def calculate_lapse_risk(
        self,
        logs: List[Dict],
        current_streak: int,
        days_tracked: int
    ) -> Tuple[float, str]:
        """
        Calculate risk of breaking habit (0-1) and risk level
        
        Returns: (risk_score, risk_level)
        """
        
        risk_factors = []
        
        # 1. Streak length (longer = lower risk)
        if current_streak < 7:
            risk_factors.append(0.7)  # High risk in first week
        elif current_streak < 21:
            risk_factors.append(0.5)  # Medium risk in first 3 weeks
        elif current_streak < 66:
            risk_factors.append(0.3)  # Lower risk but not automatic
        else:
            risk_factors.append(0.1)  # Low risk when automated
        
        # 2. Recent consistency
        if len(logs) >= 7:
            recent_logs = logs[-7:]
            recent_days = len(set(log['date'].split('T')[0] for log in recent_logs))
            recent_consistency = recent_days / 7
            inconsistency_risk = 1 - recent_consistency
            risk_factors.append(inconsistency_risk)
        
        # 3. Trend direction
        if len(logs) >= 14:
            mid = len(logs) // 2
            first_half_rate = len(logs[:mid]) / (days_tracked / 2)
            second_half_rate = len(logs[mid:]) / (days_tracked / 2)
            
            if second_half_rate < first_half_rate:
                risk_factors.append(0.6)  # Declining trend
            else:
                risk_factors.append(0.2)  # Improving trend
        
        # Average risk
        risk_score = statistics.mean(risk_factors) if risk_factors else 0.5
        
        # Determine level
        if risk_score >= 0.7:
            risk_level = 'high'
        elif risk_score >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return risk_score, risk_level
    
    def predict_success_probability(
        self,
        habit_strength: float,
        automaticity: float,
        lapse_risk: float
    ) -> Dict[str, float]:
        """
        Predict probability of long-term success
        
        Returns probabilities for different timeframes
        """
        
        # Base success probability
        base_success = (habit_strength / 100 + automaticity + (1 - lapse_risk)) / 3
        
        # Time-decay factors
        probabilities = {
            '1_week': base_success * 0.95,
            '1_month': base_success * 0.85,
            '3_months': base_success * 0.75,
            '6_months': base_success * 0.70,
            '1_year': base_success * 0.65
        }
        
        return {k: round(min(1.0, v), 2) for k, v in probabilities.items()}
    
    def identify_behavior_stage(
        self,
        current_streak: int,
        habit_strength: float,
        logs: List[Dict]
    ) -> str:
        """
        Identify current stage in behavior change model
        """
        
        if not logs:
            return 'precontemplation'
        
        if current_streak == 0 and len(logs) < 3:
            return 'contemplation'
        
        if current_streak < 7:
            return 'preparation'
        
        if current_streak < 21:
            return 'action'
        
        if current_streak >= 21 and habit_strength >= 60:
            return 'maintenance'
        
        if current_streak >= 180 and habit_strength >= 80:
            return 'termination'  # Habit fully integrated
        
        return 'action'
    
    def calculate_relapse_triggers(
        self,
        logs: List[Dict],
        failed_days: List[datetime]
    ) -> List[Dict]:
        """
        Identify patterns in failed attempts
        
        Returns triggers that correlate with lapses
        """
        
        triggers = []
        
        if not failed_days:
            return triggers
        
        # Analyze day of week patterns
        failed_weekdays = Counter([d.weekday() for d in failed_days])
        total_weeks = len(logs) / 7 if logs else 1
        
        for weekday, count in failed_weekdays.items():
            rate = count / total_weeks
            if rate > 0.5:  # More than 50% failure rate
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                triggers.append({
                    'type': 'day_of_week',
                    'value': day_names[weekday],
                    'frequency': round(rate, 2),
                    'recommendation': f'Set extra reminders for {day_names[weekday]}s'
                })
        
        # Time-based patterns
        failed_hours = []
        for log in logs:
            dt = datetime.fromisoformat(log['date'].replace('Z', ''))
            if dt.date() in [f.date() for f in failed_days]:
                failed_hours.append(dt.hour)
        
        if failed_hours:
            common_hour = Counter(failed_hours).most_common(1)[0][0]
            triggers.append({
                'type': 'time_of_day',
                'value': f'{common_hour}:00',
                'frequency': len(failed_hours) / len(failed_days),
                'recommendation': 'Consider shifting habit to a different time'
            })
        
        return triggers
    
    def generate_behavior_change_plan(
        self,
        habit_type: str,
        current_stage: str,
        habit_strength: float
    ) -> Dict:
        """
        Generate personalized behavior change plan
        
        Based on Transtheoretical Model and Implementation Intentions
        """
        
        plan = {
            'current_stage': current_stage,
            'next_stage': '',
            'strategies': [],
            'micro_goals': [],
            'environmental_design': [],
            'if_then_plans': []
        }
        
        # Stage-specific strategies
        if current_stage == 'contemplation':
            plan['next_stage'] = 'preparation'
            plan['strategies'] = [
                'Set clear, specific goals',
                'Identify benefits of the habit',
                'Remove barriers to starting'
            ]
            plan['micro_goals'] = [
                'Complete habit 1 time this week',
                'Prepare necessary equipment/environment'
            ]
        
        elif current_stage == 'preparation':
            plan['next_stage'] = 'action'
            plan['strategies'] = [
                'Start small and build gradually',
                'Link habit to existing routine (habit stacking)',
                'Track every attempt'
            ]
            plan['micro_goals'] = [
                'Complete habit 3 times this week',
                'Establish consistent time/place'
            ]
        
        elif current_stage == 'action':
            plan['next_stage'] = 'maintenance'
            plan['strategies'] = [
                'Focus on consistency over intensity',
                'Celebrate small wins',
                'Prepare for setbacks'
            ]
            plan['micro_goals'] = [
                'Reach 21-day streak',
                'Maintain 80% weekly completion rate'
            ]
        
        elif current_stage == 'maintenance':
            plan['next_stage'] = 'termination'
            plan['strategies'] = [
                'Maintain habit strength through variation',
                'Help others build similar habits',
                'Integrate into identity'
            ]
            plan['micro_goals'] = [
                'Reach 66-day automaticity threshold',
                'Maintain 90%+ completion rate'
            ]
        
        # Implementation intentions (if-then plans)
        plan['if_then_plans'] = self._generate_if_then_plans(habit_type, current_stage)
        
        # Environmental design
        plan['environmental_design'] = self._generate_environment_design(habit_type)
        
        return plan
    
    def calculate_habit_momentum(
        self,
        logs: List[Dict],
        window_days: int = 14
    ) -> float:
        """
        Calculate current momentum (rate of improvement)
        
        Positive momentum = increasing frequency
        Negative momentum = decreasing frequency
        """
        
        if len(logs) < window_days:
            return 0.0
        
        recent_logs = logs[-window_days:]
        
        # Split into two halves
        mid = len(recent_logs) // 2
        first_half = recent_logs[:mid]
        second_half = recent_logs[mid:]
        
        # Calculate frequencies
        first_freq = len(first_half) / (window_days / 2)
        second_freq = len(second_half) / (window_days / 2)
        
        # Momentum is the difference
        momentum = second_freq - first_freq
        
        return round(momentum, 2)
    
    def predict_optimal_intervention_time(
        self,
        logs: List[Dict],
        lapse_risk: float
    ) -> Dict:
        """
        Predict when to send intervention (reminder/encouragement)
        
        Returns optimal times for different intervention types
        """
        
        # Analyze typical completion times
        hours = [datetime.fromisoformat(log['date'].replace('Z', '')).hour for log in logs]
        
        if not hours:
            return {
                'reminder_time': '09:00',
                'encouragement_time': '20:00',
                'reasoning': 'Default times (no historical data)'
            }
        
        typical_hour = Counter(hours).most_common(1)[0][0]
        
        # Reminder should be 30-60 min before typical time
        reminder_hour = (typical_hour - 1) % 24
        
        # Encouragement should be in evening if not completed
        encouragement_hour = 20
        
        return {
            'reminder_time': f'{reminder_hour:02d}:00',
            'encouragement_time': f'{encouragement_hour:02d}:00',
            'reasoning': f'Based on your typical completion at {typical_hour}:00'
        }
    
    # ==================== Private Methods ====================
    
    def _generate_if_then_plans(
        self,
        habit_type: str,
        stage: str
    ) -> List[str]:
        """Generate implementation intentions"""
        
        plans = {
            'exercise': [
                'If it\'s 7am, then I put on workout clothes',
                'If I feel tired, then I do a 10-minute walk instead',
                'If it\'s raining, then I do indoor workout'
            ],
            'meditation': [
                'If I finish breakfast, then I meditate for 5 minutes',
                'If I feel stressed, then I take 3 deep breaths',
                'If I skip morning meditation, then I meditate before bed'
            ],
            'water': [
                'If I sit at desk, then I drink water',
                'If I finish a task, then I refill water bottle',
                'If I feel hungry between meals, then I drink water first'
            ]
        }
        
        return plans.get(habit_type, [
            'If situation X occurs, then I will do habit Y',
            'If I encounter obstacle A, then I will use solution B'
        ])
    
    def _generate_environment_design(self, habit_type: str) -> List[str]:
        """Generate environmental optimization strategies"""
        
        designs = {
            'exercise': [
                'Place workout clothes next to bed',
                'Keep gym bag by front door',
                'Set out yoga mat in visible location'
            ],
            'meditation': [
                'Create dedicated meditation corner',
                'Keep meditation cushion in plain sight',
                'Use visual cue (candle, bells)'
            ],
            'study': [
                'Clear desk before each session',
                'Keep study materials organized and visible',
                'Use "do not disturb" sign'
            ],
            'water': [
                'Keep large water bottle on desk',
                'Use marked bottle with time goals',
                'Place water stations throughout home'
            ]
        }
        
        return designs.get(habit_type, ['Optimize environment for habit success'])
