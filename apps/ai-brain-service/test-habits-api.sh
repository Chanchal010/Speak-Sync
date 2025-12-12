#!/bin/bash
# Test Habit Prediction Engine Endpoints

BASE_URL="http://localhost:8000/api/habits"

echo "========================================="
echo "Testing Habit Prediction Engine"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1. Health Check"
echo "GET $BASE_URL/health"
curl -s "$BASE_URL/health" | jq .
echo ""
echo ""

# Test 2: Analyze Patterns
echo "2. Analyze Habit Patterns"
echo "POST $BASE_URL/analyze-patterns"
curl -s -X POST "$BASE_URL/analyze-patterns" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "meditation",
    "days_history": 90
  }' | jq .
echo ""
echo ""

# Test 3: Predict Streak Survival
echo "3. Predict Streak Survival"
echo "POST $BASE_URL/predict-streak"
curl -s -X POST "$BASE_URL/predict-streak" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "exercise",
    "current_streak": 14
  }' | jq .
echo ""
echo ""

# Test 4: Predict Next Completion
echo "4. Predict Next Completion Time"
echo "POST $BASE_URL/predict-next-completion"
curl -s -X POST "$BASE_URL/predict-next-completion" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "meditation"
  }' | jq .
echo ""
echo ""

# Test 5: Personalized Insights
echo "5. Get Personalized Insights"
echo "POST $BASE_URL/personalized-insights"
curl -s -X POST "$BASE_URL/personalized-insights" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "exercise"
  }' | jq .
echo ""
echo ""

# Test 6: Optimal Schedule
echo "6. Recommend Optimal Schedule"
echo "POST $BASE_URL/optimal-schedule"
curl -s -X POST "$BASE_URL/optimal-schedule" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "study"
  }' | jq .
echo ""
echo ""

# Test 7: Formation Prediction
echo "7. Predict Habit Formation"
echo "POST $BASE_URL/formation-prediction"
curl -s -X POST "$BASE_URL/formation-prediction" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "water"
  }' | jq .
echo ""
echo ""

# Test 8: Habit Strength
echo "8. Calculate Habit Strength"
echo "POST $BASE_URL/habit-strength"
curl -s -X POST "$BASE_URL/habit-strength" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "exercise",
    "days_tracked": 90
  }' | jq .
echo ""
echo ""

# Test 9: Behavior Change Plan
echo "9. Generate Behavior Change Plan"
echo "POST $BASE_URL/behavior-change-plan"
curl -s -X POST "$BASE_URL/behavior-change-plan" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "habit_type": "meditation"
  }' | jq .
echo ""
echo ""

# Test 10: Momentum
echo "10. Get Habit Momentum"
echo "GET $BASE_URL/momentum/test-user-123/exercise"
curl -s "$BASE_URL/momentum/test-user-123/exercise?window_days=14" | jq .
echo ""
echo ""

echo "========================================="
echo "✅ All Habit Prediction Tests Complete"
echo "========================================="
