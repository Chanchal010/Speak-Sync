"""
Analytics Service for cross-habit correlation analysis
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from collections import defaultdict
import statistics


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def get_correlations(
        self,
        user_id: str,
        habit_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Analyze cross-habit correlations to discover behavioral patterns
        
        Key correlations:
        1. Sleep Quality → Exercise Performance (poor sleep → high RPE)
        2. Hydration → Cognitive Performance (dehydration → mental fog)
        3. Food Satisfaction → Emotional State (low satisfaction → stress eating)
        4. Financial Stress → Sleep Quality (impulse spending → anxiety → poor sleep)
        5. Study Flow → Caffeine + Sleep (optimal conditions for deep work)
        """
        
        # Build date filter
        date_filter = {"user_id": user_id, "deleted_at": None}
        if start_date or end_date:
            date_filter["timestamp"] = {}
            if start_date:
                date_filter["timestamp"]["$gte"] = start_date
            if end_date:
                date_filter["timestamp"]["$lte"] = end_date
        
        # Fetch all log types
        sleep_logs = await self.db["sleep_logs"].find(date_filter).to_list(length=None)
        exercise_logs = await self.db["exercise_logs"].find(date_filter).to_list(length=None)
        water_logs = await self.db["water_logs"].find(date_filter).to_list(length=None)
        food_logs = await self.db["food_logs"].find(date_filter).to_list(length=None)
        financial_logs = await self.db["financial_logs"].find(date_filter).to_list(length=None)
        study_logs = await self.db["study_logs"].find(date_filter).to_list(length=None)
        
        correlations = {}
        
        # 1. Sleep Quality → Exercise Performance
        if sleep_logs and exercise_logs:
            correlations["sleep_to_exercise"] = self._analyze_sleep_exercise(
                sleep_logs, exercise_logs
            )
        
        # 2. Hydration → Cognitive Performance
        if water_logs:
            correlations["hydration_to_cognition"] = self._analyze_hydration_cognition(
                water_logs
            )
        
        # 3. Food Satisfaction → Emotional Patterns
        if food_logs:
            correlations["food_to_emotion"] = self._analyze_food_emotion(
                food_logs
            )
        
        # 4. Financial Stress → Sleep Quality
        if financial_logs and sleep_logs:
            correlations["financial_to_sleep"] = self._analyze_financial_sleep(
                financial_logs, sleep_logs
            )
        
        # 5. Study Flow → Caffeine + Sleep
        if study_logs:
            correlations["study_flow_factors"] = self._analyze_study_flow(
                study_logs, sleep_logs, water_logs
            )
        
        # 6. Cross-habit daily patterns
        correlations["daily_patterns"] = self._analyze_daily_patterns(
            sleep_logs, exercise_logs, water_logs, food_logs, study_logs
        )
        
        return {
            "user_id": user_id,
            "analysis_period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            },
            "correlations": correlations,
            "insights": self._generate_insights(correlations)
        }
    
    def _analyze_sleep_exercise(
        self, sleep_logs: List[Dict], exercise_logs: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze how sleep quality affects exercise performance"""
        
        # Group by date
        sleep_by_date = {}
        for log in sleep_logs:
            date = log["wake_time"].date() if log.get("wake_time") else log["timestamp"].date()
            sleep_by_date[date] = log
        
        exercise_by_date = defaultdict(list)
        for log in exercise_logs:
            date = log["timestamp"].date()
            exercise_by_date[date].append(log)
        
        # Find next-day correlations
        poor_sleep_high_rpe = []
        good_sleep_low_rpe = []
        
        for sleep_date, sleep_log in sleep_by_date.items():
            next_day = sleep_date + timedelta(days=1)
            if next_day in exercise_by_date:
                sleep_quality = sleep_log.get("sleep_quality", 5)
                for ex_log in exercise_by_date[next_day]:
                    rpe = ex_log.get("perceived_exertion", 5)
                    
                    if sleep_quality <= 4 and rpe >= 7:
                        poor_sleep_high_rpe.append({
                            "date": next_day.isoformat(),
                            "sleep_quality": sleep_quality,
                            "rpe": rpe,
                            "exercise_type": ex_log.get("exercise_type")
                        })
                    elif sleep_quality >= 7 and rpe <= 5:
                        good_sleep_low_rpe.append({
                            "date": next_day.isoformat(),
                            "sleep_quality": sleep_quality,
                            "rpe": rpe,
                            "exercise_type": ex_log.get("exercise_type")
                        })
        
        return {
            "pattern": "Poor sleep correlates with higher perceived exertion next day",
            "poor_sleep_high_rpe_instances": len(poor_sleep_high_rpe),
            "good_sleep_low_rpe_instances": len(good_sleep_low_rpe),
            "examples": poor_sleep_high_rpe[:3],
            "strength": "moderate" if len(poor_sleep_high_rpe) >= 3 else "weak"
        }
    
    def _analyze_hydration_cognition(self, water_logs: List[Dict]) -> Dict[str, Any]:
        """Analyze hydration's impact on cognitive performance"""
        
        dehydrated_with_fog = []
        hydrated_no_fog = []
        
        for log in water_logs:
            urine_color = log.get("urine_color")
            cognitive_fog = log.get("cognitive_fog", False)
            mental_clarity = log.get("mental_clarity")
            
            if urine_color and urine_color >= 5 and cognitive_fog:
                dehydrated_with_fog.append({
                    "timestamp": log["timestamp"].isoformat(),
                    "urine_color": urine_color,
                    "mental_clarity": mental_clarity,
                    "energy_level": log.get("energy_level")
                })
            elif urine_color and urine_color <= 3 and not cognitive_fog:
                hydrated_no_fog.append({
                    "timestamp": log["timestamp"].isoformat(),
                    "urine_color": urine_color,
                    "mental_clarity": mental_clarity,
                    "energy_level": log.get("energy_level")
                })
        
        # Calculate average mental clarity difference
        avg_clarity_dehydrated = (
            statistics.mean([x["mental_clarity"] for x in dehydrated_with_fog if x["mental_clarity"]])
            if dehydrated_with_fog and any(x["mental_clarity"] for x in dehydrated_with_fog)
            else None
        )
        avg_clarity_hydrated = (
            statistics.mean([x["mental_clarity"] for x in hydrated_no_fog if x["mental_clarity"]])
            if hydrated_no_fog and any(x["mental_clarity"] for x in hydrated_no_fog)
            else None
        )
        
        return {
            "pattern": "Dehydration strongly correlates with cognitive fog and reduced mental clarity",
            "dehydrated_with_fog": len(dehydrated_with_fog),
            "hydrated_clear_mind": len(hydrated_no_fog),
            "avg_mental_clarity_when_dehydrated": round(avg_clarity_dehydrated, 2) if avg_clarity_dehydrated else None,
            "avg_mental_clarity_when_hydrated": round(avg_clarity_hydrated, 2) if avg_clarity_hydrated else None,
            "clarity_difference": round(avg_clarity_hydrated - avg_clarity_dehydrated, 2) if avg_clarity_hydrated and avg_clarity_dehydrated else None,
            "examples": dehydrated_with_fog[:3],
            "strength": "strong" if len(dehydrated_with_fog) >= 2 else "weak"
        }
    
    def _analyze_food_emotion(self, food_logs: List[Dict]) -> Dict[str, Any]:
        """Analyze food satisfaction and emotional eating patterns"""
        
        low_satisfaction_emotional = []
        high_satisfaction_content = []
        
        for log in food_logs:
            satisfaction = log.get("satisfaction_level")
            emotional_state = log.get("emotional_state_before")
            ate_alone = log.get("ate_alone", False)
            
            if satisfaction and satisfaction <= 4 and emotional_state in ["stressed", "sad", "anxious", "bored"]:
                low_satisfaction_emotional.append({
                    "timestamp": log["timestamp"].isoformat(),
                    "meal_type": log.get("meal_type"),
                    "satisfaction": satisfaction,
                    "emotional_state": emotional_state,
                    "ate_alone": ate_alone
                })
            elif satisfaction and satisfaction >= 8 and emotional_state in ["happy", "content", "energetic"]:
                high_satisfaction_content.append({
                    "timestamp": log["timestamp"].isoformat(),
                    "meal_type": log.get("meal_type"),
                    "satisfaction": satisfaction,
                    "emotional_state": emotional_state
                })
        
        return {
            "pattern": "Low meal satisfaction correlates with negative emotional states",
            "low_satisfaction_negative_emotion": len(low_satisfaction_emotional),
            "high_satisfaction_positive_emotion": len(high_satisfaction_content),
            "examples": low_satisfaction_emotional[:3],
            "strength": "moderate" if len(low_satisfaction_emotional) >= 3 else "weak"
        }
    
    def _analyze_financial_sleep(
        self, financial_logs: List[Dict], sleep_logs: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze how financial stress affects sleep quality"""
        
        # Group by date
        financial_by_date = defaultdict(list)
        for log in financial_logs:
            date = log["timestamp"].date()
            financial_by_date[date].append(log)
        
        sleep_by_date = {}
        for log in sleep_logs:
            date = log["bedtime"].date() if log.get("bedtime") else log["timestamp"].date()
            sleep_by_date[date] = log
        
        impulse_poor_sleep = []
        
        for fin_date, fin_logs in financial_by_date.items():
            # Check if there were impulse purchases
            impulse_purchases = [log for log in fin_logs if log.get("impulse_buy")]
            if impulse_purchases and fin_date in sleep_by_date:
                sleep_log = sleep_by_date[fin_date]
                sleep_quality = sleep_log.get("sleep_quality", 5)
                
                if sleep_quality <= 5:
                    total_impulse = sum(log.get("amount") or 0 for log in impulse_purchases)
                    impulse_poor_sleep.append({
                        "date": fin_date.isoformat(),
                        "impulse_purchase_count": len(impulse_purchases),
                        "total_impulse_amount": total_impulse,
                        "sleep_quality": sleep_quality,
                        "stress_level": sleep_log.get("stress_level")
                    })
        
        return {
            "pattern": "Impulse spending days correlate with poor sleep quality",
            "impulse_spending_poor_sleep": len(impulse_poor_sleep),
            "examples": impulse_poor_sleep[:3],
            "strength": "moderate" if len(impulse_poor_sleep) >= 2 else "weak"
        }
    
    def _analyze_study_flow(
        self, study_logs: List[Dict], sleep_logs: List[Dict], water_logs: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze factors contributing to study flow state"""
        
        high_flow_sessions = []
        low_flow_sessions = []
        
        # Group sleep by date
        sleep_by_date = {}
        for log in sleep_logs:
            date = log["wake_time"].date() if log.get("wake_time") else log["timestamp"].date()
            sleep_by_date[date] = log
        
        # Group water logs by date
        water_by_date = defaultdict(list)
        for log in water_logs:
            date = log["timestamp"].date()
            water_by_date[date].append(log)
        
        for study_log in study_logs:
            flow_score = study_log.get("flow_state_score")
            study_date = study_log["scheduled_start"].date() if study_log.get("scheduled_start") else study_log["timestamp"].date()
            
            # Get sleep quality from previous night
            prev_sleep = sleep_by_date.get(study_date)
            sleep_quality = prev_sleep.get("sleep_quality") if prev_sleep else None
            
            # Get hydration on study day
            day_water_logs = water_by_date.get(study_date, [])
            avg_urine_color = (
                statistics.mean([log.get("urine_color") for log in day_water_logs if log.get("urine_color")])
                if day_water_logs
                else None
            )
            total_caffeine = sum(log.get("caffeine_intake") or 0 for log in day_water_logs)
            
            session_data = {
                "timestamp": study_log["timestamp"].isoformat(),
                "flow_score": flow_score,
                "sleep_quality": sleep_quality,
                "hydration_status": "optimal" if avg_urine_color and avg_urine_color <= 3 else "dehydrated" if avg_urine_color and avg_urine_color >= 5 else "adequate",
                "caffeine_intake": total_caffeine,
                "location": study_log.get("location"),
                "used_music": study_log.get("used_music"),
                "stickiness_percentage": study_log.get("stickiness_percentage")
            }
            
            if flow_score and flow_score >= 8:
                high_flow_sessions.append(session_data)
            elif flow_score and flow_score <= 4:
                low_flow_sessions.append(session_data)
        
        # Identify optimal conditions for high flow
        optimal_conditions = {}
        if high_flow_sessions:
            optimal_conditions["avg_sleep_quality"] = round(
                statistics.mean([s["sleep_quality"] for s in high_flow_sessions if s["sleep_quality"]]), 2
            ) if any(s["sleep_quality"] for s in high_flow_sessions) else None
            
            optimal_conditions["avg_caffeine"] = round(
                statistics.mean([s["caffeine_intake"] for s in high_flow_sessions if s["caffeine_intake"]]), 2
            ) if any(s["caffeine_intake"] for s in high_flow_sessions) else None
            
            optimal_conditions["most_common_location"] = max(
                set([s["location"] for s in high_flow_sessions if s["location"]]),
                key=[s["location"] for s in high_flow_sessions if s["location"]].count
            ) if any(s["location"] for s in high_flow_sessions) else None
        
        return {
            "pattern": "High flow states correlate with good sleep, optimal hydration, and environmental factors",
            "high_flow_sessions": len(high_flow_sessions),
            "low_flow_sessions": len(low_flow_sessions),
            "optimal_conditions_for_flow": optimal_conditions,
            "high_flow_examples": high_flow_sessions[:3],
            "strength": "strong" if len(high_flow_sessions) >= 2 else "weak"
        }
    
    def _analyze_daily_patterns(
        self,
        sleep_logs: List[Dict],
        exercise_logs: List[Dict],
        water_logs: List[Dict],
        food_logs: List[Dict],
        study_logs: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze overall daily habit patterns"""
        
        # Group all logs by date
        dates_with_data = set()
        for logs in [sleep_logs, exercise_logs, water_logs, food_logs, study_logs]:
            for log in logs:
                date = log["timestamp"].date()
                dates_with_data.add(date)
        
        complete_days = []
        for date in dates_with_data:
            has_sleep = any(log["timestamp"].date() == date for log in sleep_logs)
            has_exercise = any(log["timestamp"].date() == date for log in exercise_logs)
            has_water = any(log["timestamp"].date() == date for log in water_logs)
            has_food = any(log["timestamp"].date() == date for log in food_logs)
            has_study = any(log["timestamp"].date() == date for log in study_logs)
            
            habit_count = sum([has_sleep, has_exercise, has_water, has_food, has_study])
            
            if habit_count >= 3:
                complete_days.append({
                    "date": date.isoformat(),
                    "has_sleep": has_sleep,
                    "has_exercise": has_exercise,
                    "has_water": has_water,
                    "has_food": has_food,
                    "has_study": has_study
                })
        
        return {
            "total_days_tracked": len(dates_with_data),
            "days_with_multiple_habits": len(complete_days),
            "tracking_consistency": round(len(complete_days) / len(dates_with_data) * 100, 2) if dates_with_data else 0,
            "recent_complete_days": complete_days[-5:] if complete_days else []
        }
    
    def _generate_insights(self, correlations: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from correlations"""
        insights = []
        
        # Sleep-Exercise insight
        if "sleep_to_exercise" in correlations:
            data = correlations["sleep_to_exercise"]
            if data.get("strength") in ["moderate", "strong"]:
                insights.append(
                    f"💤 Your exercise performance is {data['poor_sleep_high_rpe_instances']}x harder after poor sleep. "
                    "Prioritize 7-8 hours for better workouts."
                )
        
        # Hydration-Cognition insight
        if "hydration_to_cognition" in correlations:
            data = correlations["hydration_to_cognition"]
            if data.get("strength") in ["moderate", "strong"] and data.get("clarity_difference"):
                insights.append(
                    f"💧 Proper hydration improves your mental clarity by {data['clarity_difference']} points. "
                    "Aim for urine color 1-3 on Armstrong Scale."
                )
        
        # Food-Emotion insight
        if "food_to_emotion" in correlations:
            data = correlations["food_to_emotion"]
            if data.get("strength") in ["moderate", "strong"]:
                insights.append(
                    f"🍽️ Low meal satisfaction correlates with negative emotions in {data['low_satisfaction_negative_emotion']} instances. "
                    "Consider meal planning when stressed."
                )
        
        # Financial-Sleep insight
        if "financial_to_sleep" in correlations:
            data = correlations["financial_to_sleep"]
            if data.get("strength") in ["moderate", "strong"]:
                insights.append(
                    f"💰 Impulse spending days correlate with poor sleep in {data['impulse_spending_poor_sleep']} cases. "
                    "Financial stress may be affecting your rest."
                )
        
        # Study Flow insight
        if "study_flow_factors" in correlations:
            data = correlations["study_flow_factors"]
            if data.get("strength") in ["moderate", "strong"]:
                optimal = data.get("optimal_conditions_for_flow", {})
                if optimal.get("most_common_location"):
                    insights.append(
                        f"📚 Your best study sessions happen at {optimal['most_common_location']} "
                        f"with {optimal.get('avg_caffeine', 0):.0f}mg caffeine and sleep quality {optimal.get('avg_sleep_quality', 0):.1f}/10."
                    )
        
        # Daily patterns insight
        if "daily_patterns" in correlations:
            data = correlations["daily_patterns"]
            if data.get("tracking_consistency", 0) >= 70:
                insights.append(
                    f"✨ Great consistency! You're tracking multiple habits {data['tracking_consistency']:.0f}% of days."
                )
        
        return insights
