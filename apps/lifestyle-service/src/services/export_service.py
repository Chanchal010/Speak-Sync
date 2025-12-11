"""
Export Service for habit data export in CSV/JSON formats
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import csv
import json
from io import StringIO


class ExportService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def export_data(
        self,
        user_id: str,
        format: str = "csv",
        habit_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Export habit data in CSV or JSON format
        
        Args:
            user_id: User identifier
            format: Export format ('csv' or 'json')
            habit_types: Filter by specific habit types (food, exercise, financial, sleep, study, water)
            start_date: Filter logs from this date onwards
            end_date: Filter logs until this date
        
        Returns:
            Dict containing exported data with metadata
        """
        
        # Build date filter
        date_filter = {"user_id": user_id, "deleted_at": None}
        if start_date or end_date:
            date_filter["timestamp"] = {}
            if start_date:
                date_filter["timestamp"]["$gte"] = start_date
            if end_date:
                date_filter["timestamp"]["$lte"] = end_date
        
        # Determine which habit types to export
        types_to_export = habit_types if habit_types else ["food", "exercise", "financial", "sleep", "study", "water"]
        
        export_data = {}
        
        # Export each habit type
        for habit_type in types_to_export:
            collection_name = f"{habit_type}_logs"
            logs = await self.db[collection_name].find(date_filter).to_list(length=None)
            
            if logs:
                # Add calculated fields based on habit type
                processed_logs = self._add_calculated_fields(logs, habit_type)
                export_data[habit_type] = processed_logs
        
        # Format the data
        if format.lower() == "csv":
            return self._format_as_csv(export_data)
        else:
            return self._format_as_json(export_data)
    
    def _add_calculated_fields(self, logs: List[Dict], habit_type: str) -> List[Dict]:
        """Add calculated fields to logs based on habit type"""
        
        processed_logs = []
        for log in logs:
            processed_log = dict(log)
            
            # Convert ObjectId to string
            processed_log["_id"] = str(processed_log.get("_id", ""))
            
            # Convert datetime objects to ISO format strings
            for field in ["timestamp", "created_at", "updated_at", "bedtime", "wake_time", "scheduled_start", "scheduled_end", "actual_start", "actual_end"]:
                if field in processed_log and processed_log[field]:
                    processed_log[field] = processed_log[field].isoformat() if hasattr(processed_log[field], 'isoformat') else str(processed_log[field])
            
            # Add habit-specific calculated fields
            if habit_type == "sleep":
                # Add chronotype hint
                if processed_log.get("bedtime") and processed_log.get("wake_time"):
                    bedtime_str = processed_log["bedtime"]
                    wake_str = processed_log["wake_time"]
                    try:
                        bedtime_hour = datetime.fromisoformat(bedtime_str).hour
                        wake_hour = datetime.fromisoformat(wake_str).hour
                        
                        if bedtime_hour < 22 and wake_hour < 6:
                            processed_log["chronotype_hint"] = "early_bird"
                        elif bedtime_hour >= 24 or (bedtime_hour == 0 and wake_hour > 8):
                            processed_log["chronotype_hint"] = "night_owl"
                        else:
                            processed_log["chronotype_hint"] = "intermediate"
                    except:
                        processed_log["chronotype_hint"] = "unknown"
                
                # Add sleep debt
                target_hours = processed_log.get("target_hours", 8)
                duration = processed_log.get("duration")
                if duration:
                    processed_log["sleep_debt"] = round(target_hours - duration, 2)
            
            elif habit_type == "study":
                # Stickiness percentage already calculated and stored
                pass
            
            elif habit_type == "water":
                # Add hydration status
                urine_color = processed_log.get("urine_color")
                if urine_color:
                    if urine_color <= 3:
                        processed_log["hydration_status"] = "optimal"
                    elif urine_color == 4:
                        processed_log["hydration_status"] = "adequate"
                    elif urine_color in [5, 6]:
                        processed_log["hydration_status"] = "mild_dehydration"
                    elif urine_color == 7:
                        processed_log["hydration_status"] = "moderate_dehydration"
                    elif urine_color == 8:
                        processed_log["hydration_status"] = "severe_dehydration"
                    else:
                        processed_log["hydration_status"] = "unknown"
            
            elif habit_type == "exercise":
                # Add over-training indicator
                rpe = processed_log.get("perceived_exertion")
                post_energy = processed_log.get("energy_level_post")
                soreness = processed_log.get("soreness_level")
                
                if rpe and post_energy and soreness:
                    if rpe >= 9 and post_energy <= 4 and soreness >= 7:
                        processed_log["over_training_risk"] = "high"
                    elif rpe >= 8 and post_energy <= 5:
                        processed_log["over_training_risk"] = "moderate"
                    else:
                        processed_log["over_training_risk"] = "low"
            
            elif habit_type == "financial":
                # Add spending pattern
                if processed_log.get("impulse_buy"):
                    processed_log["spending_pattern"] = "impulse"
                elif processed_log.get("necessity_score", 0) >= 8:
                    processed_log["spending_pattern"] = "necessary"
                else:
                    processed_log["spending_pattern"] = "discretionary"
            
            processed_logs.append(processed_log)
        
        return processed_logs
    
    def _format_as_csv(self, export_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Format export data as CSV (one CSV per habit type)"""
        
        csv_files = {}
        
        for habit_type, logs in export_data.items():
            if not logs:
                continue
            
            # Get all unique field names
            all_fields = set()
            for log in logs:
                all_fields.update(log.keys())
            
            # Sort fields for consistent ordering
            fields = sorted(list(all_fields))
            
            # Create CSV content
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            
            for log in logs:
                # Convert None values to empty strings for CSV
                row = {k: (v if v is not None else "") for k, v in log.items()}
                writer.writerow(row)
            
            csv_files[f"{habit_type}_logs.csv"] = output.getvalue()
        
        return {
            "format": "csv",
            "files": csv_files,
            "total_logs": sum(len(logs) for logs in export_data.values()),
            "habit_types": list(export_data.keys())
        }
    
    def _format_as_json(self, export_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Format export data as JSON"""
        
        # Convert to JSON-serializable format
        json_data = {}
        for habit_type, logs in export_data.items():
            json_data[habit_type] = logs
        
        return {
            "format": "json",
            "data": json_data,
            "total_logs": sum(len(logs) for logs in export_data.values()),
            "habit_types": list(export_data.keys()),
            "exported_at": datetime.utcnow().isoformat()
        }
