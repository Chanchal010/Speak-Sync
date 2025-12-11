#!/bin/bash
# Test Smart Scheduling AI Endpoints

BASE_URL="http://localhost:8000/api/scheduling"

echo "========================================="
echo "Testing Smart Scheduling AI Endpoints"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1. Health Check"
echo "GET $BASE_URL/health"
curl -s "$BASE_URL/health" | jq .
echo ""
echo ""

# Test 2: Analyze Conflicts
echo "2. Analyze Schedule Conflicts"
echo "POST $BASE_URL/analyze-conflicts"
curl -s -X POST "$BASE_URL/analyze-conflicts" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "start_date": "2025-12-11T00:00:00Z",
    "end_date": "2025-12-18T23:59:59Z"
  }' | jq .
echo ""
echo ""

# Test 3: Suggest Time Slot
echo "3. Suggest Optimal Time Slots"
echo "POST $BASE_URL/suggest-time-slot"
curl -s -X POST "$BASE_URL/suggest-time-slot" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "task_type": "deep_work",
    "duration_minutes": 120,
    "deadline": "2025-12-20T17:00:00Z",
    "preferred_days": [1, 2, 3]
  }' | jq .
echo ""
echo ""

# Test 4: Smart Suggestions
echo "4. Get Proactive Suggestions"
echo "POST $BASE_URL/smart-suggestions"
curl -s -X POST "$BASE_URL/smart-suggestions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "context": {
      "current_time": "2025-12-11T10:00:00Z",
      "location": "office"
    }
  }' | jq .
echo ""
echo ""

# Test 5: Predict Completion Time
echo "5. Predict Task Completion Time"
echo "POST $BASE_URL/predict-completion-time"
curl -s -X POST "$BASE_URL/predict-completion-time" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "task": {
      "title": "Write documentation for scheduling API",
      "estimated_duration": 60
    }
  }' | jq .
echo ""
echo ""

# Test 6: Calculate Scheduling Score
echo "6. Calculate Scheduling Score"
echo "POST $BASE_URL/calculate-scheduling-score"
curl -s -X POST "$BASE_URL/calculate-scheduling-score" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "task": {
      "title": "Deep work session on ML model",
      "priority": "HIGH",
      "due_date": "2025-12-20T17:00:00Z"
    },
    "proposed_time": "2025-12-15T10:00:00Z",
    "current_schedule": []
  }' | jq .
echo ""
echo ""

echo "========================================="
echo "✅ All Smart Scheduling AI Tests Complete"
echo "========================================="
