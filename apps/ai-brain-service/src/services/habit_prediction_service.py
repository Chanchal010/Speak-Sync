"""
Habit Prediction Service - AI-powered habit analysis and predictions
Provides behavioral insights, streak predictions, and personalized recommendations
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import statistics
import httpx


class HabitPredictionService:
    """
    Intelligent habit analysis with predictive analytics
    """
    
    def __init__(self, lifestyle_service_url: str = "http://localhost:8001"):
        self.lifestyle_url = lifestyle_service_url
        
        # Habit type characteristics
        self.habit_characteristics = {
            'food': {
                'optimal_frequency': 'daily',
                'typical_duration': 30,  # minutes
                'best_times': [7, 8, 12, 13, 18, 19],  # meal times
                'minimum_gap': 180  # 3 hours between meals
            },
            'exercise': {
                'optimal_frequency': '3-5x/week',
                'typical_duration': 45,
                'best_times': [6, 7, 17, 18],  # morning or evening
                'rest_days_needed': True
            },
            'meditation': {
                'optimal_frequency': 'daily',
                'typical_duration': 15,
                'best_times': [6, 7, 8, 20, 21],  # morning or before bed
                'consistency_critical': True
            },
            'sleep': {
                'optimal_frequency': 'daily',
                'typical_duration': 480,  # 8 hours
                'best_times': [22, 23],  # bedtime
                'consistency_critical': True
            },
            'water': {
                'optimal_frequency': 'multiple_daily',
                'typical_duration': 2,
                'best_times': list(range(6, 22)),  # throughout day
                'minimum_gap': 30  # 30 min between drinks
            },
            'study': {
                'optimal_frequency': 'daily',
                'typical_duration': 90,
                'best_times': [9, 10, 14, 15, 16],  # peak focus
                'breaks_needed': True
            }
        }
    
    async def analyze_habit_patterns(
        self,
        user_id: str,
        habit_type: str,
        days_history: int = 90
    ) -> Dict:
        """
        Analyze user's habit patterns and behavioral trends
        
        Returns:
            {
                'completion_rate': 0.85,
                'streak_info': {
                    'current': 7,
                    'longest': 21,
                    'average': 5.3
                },
                'time_patterns': {
                    'preferred_hours': [7, 8, 9],
                    'preferred_days': [1, 2, 3, 4, 5],
                    'consistency_score': 0.78
                },
                'trends': {
                    'direction': 'improving',
                    'momentum': 0.15,
                    'stability': 0.82
                },
                'risk_factors': [
                    {
                        'type': 'weekend_dropoff',
                        'severity': 'medium',
                        'description': 'Completion drops 40% on weekends'
                    }
                ]
            }
        """
        
        # Fetch habit logs from Lifestyle Service
        logs = await self._fetch_habit_logs(user_id, habit_type, days_history)
        
        if not logs:
            return {
                'completion_rate': 0.0,
                'streak_info': {'current': 0, 'longest': 0, 'average': 0},
                'time_patterns': {},
                'trends': {'direction': 'no_data', 'momentum': 0, 'stability': 0},
                'risk_factors': []
            }
        
        # Calculate completion rate
        total_days = days_history
        logged_days = len(set(log['date'].split('T')[0] for log in logs))
        completion_rate = logged_days / total_days
        
        # Analyze streaks
        streak_info = self._analyze_streaks(logs)
        
        # Analyze time patterns
        time_patterns = self._analyze_time_patterns(logs)
        
        # Detect trends
        trends = self._detect_trends(logs, days_history)
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(logs, completion_rate, time_patterns)
        
        return {
            'completion_rate': round(completion_rate, 2),
            'streak_info': streak_info,
            'time_patterns': time_patterns,
            'trends': trends,
            'risk_factors': risk_factors
        }
    
    async def predict_streak_survival(
        self,
        user_id: str,
        habit_type: str,
        current_streak: int
    ) -> Dict:
        """
        Predict probability of maintaining current streak
        
        Returns:
            {
                'survival_probability': {
                    '1_day': 0.92,
                    '3_days': 0.78,
                    '7_days': 0.65,
                    '30_days': 0.42
                },
                'risk_level': 'medium',
                'critical_days': [6, 7],  # Weekend risk
                'recommendations': [
                    'Set reminder for weekend mornings',
                    'Prepare environment ahead of time'
                ]
            }
        """
        
        # Fetch historical data
        logs = await self._fetch_habit_logs(user_id, habit_type, 180)
        
        # Analyze past streaks
        past_streaks = self._extract_all_streaks(logs)
        
        # Calculate survival probabilities
        survival_probs = self._calculate_survival_probability(
            current_streak, 
            past_streaks
        )
        
        # Determine risk level
        avg_7day_prob = survival_probs.get('7_days', 0.5)
        if avg_7day_prob >= 0.75:
            risk_level = 'low'
        elif avg_7day_prob >= 0.50:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # Identify critical days
        critical_days = self._identify_critical_days(logs)
        
        # Generate recommendations
        recommendations = self._generate_streak_recommendations(
            risk_level, 
            critical_days,
            habit_type
        )
        
        return {
            'survival_probability': survival_probs,
            'risk_level': risk_level,
            'critical_days': critical_days,
            'recommendations': recommendations
        }
    
    async def predict_next_completion(
        self,
        user_id: str,
        habit_type: str
    ) -> Dict:
        """
        Predict when user is most likely to complete habit next
        
        Returns:
            {
                'most_likely_time': '2025-12-12T08:00:00Z',
                'confidence': 0.87,
                'alternative_times': [
                    {'time': '2025-12-12T07:30:00Z', 'probability': 0.65},
                    {'time': '2025-12-12T09:00:00Z', 'probability': 0.52}
                ],
                'reasoning': 'Based on 85% completion rate at 8am on weekdays'
            }
        """
        
        # Fetch recent logs
        logs = await self._fetch_habit_logs(user_id, habit_type, 90)
        
        # Analyze completion patterns
        time_patterns = self._analyze_time_patterns(logs)
        
        # Get tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        weekday = tomorrow.weekday()
        
        # Find most probable time
        preferred_hours = time_patterns.get('preferred_hours', [9])
        most_likely_hour = preferred_hours[0] if preferred_hours else 9
        
        most_likely_time = tomorrow.replace(
            hour=most_likely_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # Calculate confidence
        consistency = time_patterns.get('consistency_score', 0.5)
        day_completion_rate = time_patterns.get('day_completion_rates', {}).get(weekday, 0.5)
        confidence = (consistency + day_completion_rate) / 2
        
        # Generate alternatives
        alternatives = []
        for hour in preferred_hours[1:4]:  # Top 3 alternatives
            alt_time = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
            alt_prob = confidence * 0.75  # Slightly lower
            alternatives.append({
                'time': alt_time.isoformat() + 'Z',
                'probability': round(alt_prob, 2)
            })
        
        reasoning = f"Based on {int(consistency*100)}% consistency at {most_likely_hour}:00 on {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][weekday]}s"
        
        return {
            'most_likely_time': most_likely_time.isoformat() + 'Z',
            'confidence': round(confidence, 2),
            'alternative_times': alternatives,
            'reasoning': reasoning
        }
    
    async def generate_personalized_insights(
        self,
        user_id: str,
        habit_type: Optional[str] = None
    ) -> List[str]:
        """
        Generate natural language insights about user's habits
        
        Returns:
            [
                "Your meditation streak is 85% longer on weeks when you exercise",
                "You're 3x more likely to complete workouts on Monday mornings",
                "Weekend sleep consistency has improved 40% this month"
            ]
        """
        
        insights = []
        
        if habit_type:
            habit_types = [habit_type]
        else:
            habit_types = ['food', 'exercise', 'meditation', 'sleep', 'water', 'study']
        
        for h_type in habit_types:
            # Fetch data
            logs = await self._fetch_habit_logs(user_id, h_type, 90)
            if not logs:
                continue
            
            # Generate insights for this habit
            habit_insights = await self._generate_habit_specific_insights(
                user_id, h_type, logs
            )
            insights.extend(habit_insights)
        
        # Cross-habit correlations
        cross_insights = await self._analyze_habit_correlations(user_id)
        insights.extend(cross_insights)
        
        return insights[:10]  # Top 10 most interesting
    
    async def recommend_optimal_schedule(
        self,
        user_id: str,
        habit_type: str
    ) -> Dict:
        """
        Recommend optimal schedule for a habit based on user patterns
        
        Returns:
            {
                'recommended_times': [
                    {
                        'time': '08:00',
                        'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                        'confidence': 0.89,
                        'reason': 'Highest completion rate and consistency'
                    }
                ],
                'frequency': 'daily',
                'duration_recommendation': 30,
                'environment_tips': [
                    'Prepare workout clothes the night before',
                    'Set alarm 30 minutes earlier'
                ]
            }
        """
        
        # Fetch historical data
        logs = await self._fetch_habit_logs(user_id, habit_type, 90)
        patterns = self._analyze_time_patterns(logs)
        
        # Get habit characteristics
        characteristics = self.habit_characteristics.get(habit_type, {})
        
        # Determine recommended times
        preferred_hours = patterns.get('preferred_hours', characteristics.get('best_times', [9]))
        preferred_days = patterns.get('preferred_days', [0, 1, 2, 3, 4])  # Default weekdays
        
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        recommended_days = [day_names[d] for d in preferred_days[:5]]
        
        recommended_times = [{
            'time': f"{preferred_hours[0]:02d}:00" if preferred_hours else "09:00",
            'days': recommended_days,
            'confidence': patterns.get('consistency_score', 0.7),
            'reason': 'Highest completion rate and consistency based on your history'
        }]
        
        # Frequency recommendation
        actual_frequency = len(logs) / 90 * 7  # per week
        optimal_freq = characteristics.get('optimal_frequency', 'daily')
        
        # Duration recommendation
        avg_duration = statistics.mean([
            log.get('duration', 30) for log in logs if log.get('duration')
        ]) if any(log.get('duration') for log in logs) else characteristics.get('typical_duration', 30)
        
        # Environment tips
        environment_tips = self._generate_environment_tips(habit_type, patterns)
        
        return {
            'recommended_times': recommended_times,
            'frequency': optimal_freq,
            'duration_recommendation': int(avg_duration),
            'environment_tips': environment_tips
        }
    
    async def predict_habit_formation(
        self,
        user_id: str,
        habit_type: str
    ) -> Dict:
        """
        Predict when habit will become automatic (typically 66 days)
        
        Returns:
            {
                'days_to_automation': 42,
                'current_progress': 0.36,
                'formation_stage': 'building',
                'estimated_completion_date': '2025-01-22',
                'strength_indicators': {
                    'consistency': 0.78,
                    'automaticity': 0.42,
                    'confidence': 0.65
                },
                'next_milestone': {
                    'days': 21,
                    'description': '21-day habit formation checkpoint'
                }
            }
        """
        
        # Fetch logs
        logs = await self._fetch_habit_logs(user_id, habit_type, 180)
        
        # Calculate current streak
        streak_info = self._analyze_streaks(logs)
        current_streak = streak_info['current']
        
        # Habit formation typically takes 66 days
        FORMATION_DAYS = 66
        days_to_automation = max(0, FORMATION_DAYS - current_streak)
        progress = min(1.0, current_streak / FORMATION_DAYS)
        
        # Determine stage
        if progress < 0.20:
            stage = 'initiating'
        elif progress < 0.50:
            stage = 'building'
        elif progress < 0.80:
            stage = 'strengthening'
        else:
            stage = 'automatic'
        
        # Calculate strength indicators
        patterns = self._analyze_time_patterns(logs)
        consistency = patterns.get('consistency_score', 0.5)
        automaticity = min(1.0, progress * 1.5)  # Grows faster than linear
        confidence = (consistency + automaticity + progress) / 3
        
        # Estimated completion
        if days_to_automation > 0:
            completion_date = datetime.now() + timedelta(days=days_to_automation)
        else:
            completion_date = datetime.now()
        
        # Next milestone
        milestones = [7, 14, 21, 30, 45, 66]
        next_milestone_days = next((m for m in milestones if m > current_streak), 66)
        
        return {
            'days_to_automation': days_to_automation,
            'current_progress': round(progress, 2),
            'formation_stage': stage,
            'estimated_completion_date': completion_date.strftime('%Y-%m-%d'),
            'strength_indicators': {
                'consistency': round(consistency, 2),
                'automaticity': round(automaticity, 2),
                'confidence': round(confidence, 2)
            },
            'next_milestone': {
                'days': next_milestone_days,
                'description': f'{next_milestone_days}-day habit formation checkpoint'
            }
        }
    
    # ==================== Private Helper Methods ====================
    
    async def _fetch_habit_logs(
        self,
        user_id: str,
        habit_type: str,
        days: int
    ) -> List[Dict]:
        """Fetch habit logs from Lifestyle Service"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.lifestyle_url}/api/habits/{habit_type}/logs",
                    params={'user_id': user_id, 'days': days}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get('logs', [])
                else:
                    return []
        except Exception as e:
            print(f"Error fetching habit logs: {e}")
            return []
    
    def _analyze_streaks(self, logs: List[Dict]) -> Dict:
        """Calculate streak statistics"""
        if not logs:
            return {'current': 0, 'longest': 0, 'average': 0}
        
        # Sort logs by date
        sorted_logs = sorted(logs, key=lambda x: x.get('date', ''))
        
        # Get unique dates
        log_dates = [datetime.fromisoformat(log['date'].replace('Z', '')) for log in sorted_logs]
        unique_dates = sorted(set(d.date() for d in log_dates))
        
        # Calculate streaks
        streaks = []
        current_streak = 1
        
        for i in range(1, len(unique_dates)):
            days_diff = (unique_dates[i] - unique_dates[i-1]).days
            if days_diff == 1:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 1
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        # Check if current date is part of streak
        today = datetime.now().date()
        if unique_dates and (today - unique_dates[-1]).days <= 1:
            current = streaks[-1] if streaks else 0
        else:
            current = 0
        
        longest = max(streaks) if streaks else 0
        average = statistics.mean(streaks) if streaks else 0
        
        return {
            'current': current,
            'longest': longest,
            'average': round(average, 1)
        }
    
    def _analyze_time_patterns(self, logs: List[Dict]) -> Dict:
        """Analyze when user typically completes habits"""
        hour_counts = Counter()
        day_counts = Counter()
        day_completion = defaultdict(int)
        total_days_per_weekday = defaultdict(int)
        
        for log in logs:
            if 'date' in log:
                dt = datetime.fromisoformat(log['date'].replace('Z', ''))
                hour_counts[dt.hour] += 1
                day_counts[dt.weekday()] += 1
                day_completion[dt.weekday()] += 1
        
        # Calculate consistency score (0-1)
        if hour_counts:
            total = sum(hour_counts.values())
            top_hour_count = hour_counts.most_common(1)[0][1]
            consistency = top_hour_count / total
        else:
            consistency = 0
        
        # Day completion rates
        total_weeks = len(logs) / 7 if logs else 1
        day_completion_rates = {
            day: day_completion[day] / total_weeks
            for day in range(7)
        }
        
        return {
            'preferred_hours': [h for h, _ in hour_counts.most_common(5)],
            'preferred_days': [d for d, _ in day_counts.most_common(5)],
            'consistency_score': round(consistency, 2),
            'day_completion_rates': {k: round(v, 2) for k, v in day_completion_rates.items()}
        }
    
    def _detect_trends(self, logs: List[Dict], days_history: int) -> Dict:
        """Detect improvement or decline trends"""
        if len(logs) < 14:
            return {'direction': 'insufficient_data', 'momentum': 0, 'stability': 0}
        
        # Split into first half and second half
        mid_point = len(logs) // 2
        first_half = logs[:mid_point]
        second_half = logs[mid_point:]
        
        # Calculate completion rates
        first_rate = len(first_half) / (days_history / 2)
        second_rate = len(second_half) / (days_history / 2)
        
        # Determine direction
        change = second_rate - first_rate
        if abs(change) < 0.05:
            direction = 'stable'
        elif change > 0:
            direction = 'improving'
        else:
            direction = 'declining'
        
        # Momentum (rate of change)
        momentum = change
        
        # Stability (inverse of variance)
        # Calculate daily completion variance
        daily_counts = defaultdict(int)
        for log in logs:
            date = log.get('date', '').split('T')[0]
            daily_counts[date] += 1
        
        if len(daily_counts) > 1:
            variance = statistics.variance(daily_counts.values())
            stability = 1 / (1 + variance)
        else:
            stability = 0.5
        
        return {
            'direction': direction,
            'momentum': round(momentum, 2),
            'stability': round(stability, 2)
        }
    
    def _identify_risk_factors(
        self,
        logs: List[Dict],
        completion_rate: float,
        time_patterns: Dict
    ) -> List[Dict]:
        """Identify factors that might break habit"""
        risks = []
        
        # Weekend dropoff
        day_rates = time_patterns.get('day_completion_rates', {})
        if day_rates:
            weekend_avg = (day_rates.get(5, 0) + day_rates.get(6, 0)) / 2
            weekday_avg = sum(day_rates.get(i, 0) for i in range(5)) / 5
            
            if weekday_avg > 0 and weekend_avg / weekday_avg < 0.7:
                risks.append({
                    'type': 'weekend_dropoff',
                    'severity': 'medium',
                    'description': f'Completion drops {int((1 - weekend_avg/weekday_avg)*100)}% on weekends'
                })
        
        # Low overall completion
        if completion_rate < 0.5:
            risks.append({
                'type': 'low_completion',
                'severity': 'high',
                'description': f'Overall completion rate is only {int(completion_rate*100)}%'
            })
        
        # Inconsistent timing
        consistency = time_patterns.get('consistency_score', 1.0)
        if consistency < 0.4:
            risks.append({
                'type': 'timing_inconsistency',
                'severity': 'low',
                'description': 'No consistent time pattern established'
            })
        
        return risks
    
    def _extract_all_streaks(self, logs: List[Dict]) -> List[int]:
        """Extract all streak lengths from history"""
        if not logs:
            return []
        
        log_dates = [datetime.fromisoformat(log['date'].replace('Z', '')) for log in logs]
        unique_dates = sorted(set(d.date() for d in log_dates))
        
        streaks = []
        current_streak = 1
        
        for i in range(1, len(unique_dates)):
            if (unique_dates[i] - unique_dates[i-1]).days == 1:
                current_streak += 1
            else:
                streaks.append(current_streak)
                current_streak = 1
        
        if current_streak > 0:
            streaks.append(current_streak)
        
        return streaks
    
    def _calculate_survival_probability(
        self,
        current_streak: int,
        past_streaks: List[int]
    ) -> Dict[str, float]:
        """Calculate probability of streak surviving N more days"""
        if not past_streaks:
            # Default probabilities
            return {
                '1_day': 0.70,
                '3_days': 0.50,
                '7_days': 0.35,
                '30_days': 0.15
            }
        
        # Count how many past streaks reached each length
        targets = [1, 3, 7, 30]
        probabilities = {}
        
        for target in targets:
            target_length = current_streak + target
            reached = sum(1 for s in past_streaks if s >= target_length)
            prob = reached / len(past_streaks)
            probabilities[f'{target}_days'] = round(prob, 2)
        
        return probabilities
    
    def _identify_critical_days(self, logs: List[Dict]) -> List[int]:
        """Identify high-risk days of week"""
        day_rates = defaultdict(int)
        day_totals = defaultdict(int)
        
        for log in logs:
            dt = datetime.fromisoformat(log['date'].replace('Z', ''))
            day_rates[dt.weekday()] += 1
        
        # Calculate total possible days for each weekday
        weeks = len(logs) / 7
        for day in range(7):
            day_totals[day] = weeks
        
        # Find days with <50% completion
        critical = []
        for day in range(7):
            if day_totals[day] > 0:
                rate = day_rates[day] / day_totals[day]
                if rate < 0.5:
                    critical.append(day)
        
        return critical
    
    def _generate_streak_recommendations(
        self,
        risk_level: str,
        critical_days: List[int],
        habit_type: str
    ) -> List[str]:
        """Generate recommendations to maintain streak"""
        recommendations = []
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if critical_days:
            day_list = ', '.join(day_names[d] for d in critical_days[:3])
            recommendations.append(f'Set extra reminders for {day_list}')
        
        if risk_level == 'high':
            recommendations.append('Consider reducing difficulty temporarily')
            recommendations.append('Find an accountability partner')
        
        # Habit-specific tips
        characteristics = self.habit_characteristics.get(habit_type, {})
        if characteristics.get('consistency_critical'):
            recommendations.append('Consistency is key - do it at the same time daily')
        
        if not recommendations:
            recommendations.append('Keep up the great work!')
        
        return recommendations
    
    async def _generate_habit_specific_insights(
        self,
        user_id: str,
        habit_type: str,
        logs: List[Dict]
    ) -> List[str]:
        """Generate insights for specific habit"""
        insights = []
        
        # Analyze patterns
        patterns = self._analyze_time_patterns(logs)
        streak_info = self._analyze_streaks(logs)
        
        # Streak insights
        if streak_info['current'] >= 7:
            insights.append(
                f"Your {habit_type} streak is at {streak_info['current']} days! "
                f"That's {streak_info['current'] - streak_info['average']:.0f} days above your average."
            )
        
        # Time pattern insights
        if patterns['preferred_hours']:
            hour = patterns['preferred_hours'][0]
            insights.append(
                f"You're most consistent with {habit_type} at {hour}:00 "
                f"({int(patterns['consistency_score']*100)}% of the time)"
            )
        
        return insights
    
    async def _analyze_habit_correlations(self, user_id: str) -> List[str]:
        """Find correlations between different habits"""
        insights = []
        
        # This would analyze multiple habits and find correlations
        # For now, return placeholder
        insights.append("Keep logging to discover connections between your habits!")
        
        return insights
    
    def _generate_environment_tips(
        self,
        habit_type: str,
        patterns: Dict
    ) -> List[str]:
        """Generate environment optimization tips"""
        tips = []
        
        habit_tips = {
            'exercise': [
                'Prepare workout clothes the night before',
                'Keep gym bag by the door',
                'Set out workout equipment in advance'
            ],
            'meditation': [
                'Create a dedicated meditation space',
                'Keep meditation cushion visible',
                'Eliminate distractions beforehand'
            ],
            'study': [
                'Clear desk before study session',
                'Silence phone notifications',
                'Prepare materials in advance'
            ],
            'water': [
                'Keep water bottle on desk',
                'Set visual reminders',
                'Track intake with marked bottle'
            ]
        }
        
        return habit_tips.get(habit_type, ['Stay consistent and track your progress'])
