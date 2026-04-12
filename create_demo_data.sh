#!/bin/bash

# Get user ID
USER_ID=$(curl -s "http://localhost:3001/internal/users/email/chanchalbag115@gmail.com" \
  -H "x-internal-api-key: 96TDvSHYJATQsyzGdK2kY1WR8wp04hvrEzMoRD5uKCkTlSvIofe7uofakGdcujT9" | jq -r '.data.id')

echo "Creating demo data for user: $USER_ID"

# Create Food Habit
echo "Creating Food habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Healthy Eating",
    "habit_type": "food",
    "description": "Track my daily meals and nutrition",
    "color": "#4CAF50",
    "icon": "🍎",
    "is_active": true
  }' | jq .

# Create Exercise Habit
echo "Creating Exercise habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Daily Workout",
    "habit_type": "exercise",
    "description": "Stay fit with regular exercise",
    "color": "#FF5722",
    "icon": "🏋️",
    "is_active": true
  }' | jq .

# Create Sleep Habit
echo "Creating Sleep habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Quality Sleep",
    "habit_type": "sleep",
    "description": "Track sleep patterns for better rest",
    "color": "#9C27B0",
    "icon": "😴",
    "is_active": true
  }' | jq .

# Create Water Habit
echo "Creating Water habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Stay Hydrated",
    "habit_type": "water",
    "description": "Drink 8 glasses of water daily",
    "color": "#2196F3",
    "icon": "💧",
    "is_active": true
  }' | jq .

# Create Financial Habit
echo "Creating Financial habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Budget Tracking",
    "habit_type": "financial",
    "description": "Monitor spending and savings",
    "color": "#FFC107",
    "icon": "💰",
    "is_active": true
  }' | jq .

# Create Study Habit
echo "Creating Study habit..."
curl -s -X POST "http://localhost:8001/api/habits" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Learning Time",
    "habit_type": "study",
    "description": "Daily study and skill development",
    "color": "#673AB7",
    "icon": "📖",
    "is_active": true
  }' | jq .

echo ""
echo "Creating sample tasks..."

# Create Task Category
CATEGORY_ID=$(curl -s -X POST "http://localhost:3001/api/categories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy" \
  -H "x-user-id: $USER_ID" \
  -d '{
    "name": "Personal",
    "color": "#4CAF50",
    "icon": "person"
  }' | jq -r '.data.id')

echo "Created category: $CATEGORY_ID"

# Create Tasks
curl -s -X POST "http://localhost:3001/api/tasks" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Morning Workout\",
    \"description\": \"30 minutes cardio session\",
    \"priority\": \"high\",
    \"status\": \"pending\",
    \"categoryId\": \"$CATEGORY_ID\",
    \"dueDate\": \"$(date -u -d '+1 day' +%Y-%m-%dT09:00:00.000Z)\"
  }" | jq .

curl -s -X POST "http://localhost:3001/api/tasks" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Meal Prep Sunday\",
    \"description\": \"Prepare healthy meals for the week\",
    \"priority\": \"medium\",
    \"status\": \"pending\",
    \"categoryId\": \"$CATEGORY_ID\",
    \"dueDate\": \"$(date -u -d 'next sunday' +%Y-%m-%dT10:00:00.000Z)\"
  }" | jq .

curl -s -X POST "http://localhost:3001/api/tasks" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Review Budget\",
    \"description\": \"Check monthly expenses and savings\",
    \"priority\": \"high\",
    \"status\": \"pending\",
    \"categoryId\": \"$CATEGORY_ID\",
    \"dueDate\": \"$(date -u -d '+2 days' +%Y-%m-%dT18:00:00.000Z)\"
  }" | jq .

echo ""
echo "Creating calendar events..."

# Create Calendar Events
curl -s -X POST "http://localhost:3001/api/events" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Gym Session\",
    \"description\": \"Leg day workout\",
    \"startTime\": \"$(date -u -d 'tomorrow 06:00' +%Y-%m-%dT06:00:00.000Z)\",
    \"endTime\": \"$(date -u -d 'tomorrow 07:30' +%Y-%m-%dT07:30:00.000Z)\",
    \"location\": \"Local Gym\",
    \"isAllDay\": false
  }" | jq .

curl -s -X POST "http://localhost:3001/api/events" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Study Session\",
    \"description\": \"Flutter development practice\",
    \"startTime\": \"$(date -u -d 'tomorrow 14:00' +%Y-%m-%dT14:00:00.000Z)\",
    \"endTime\": \"$(date -u -d 'tomorrow 16:00' +%Y-%m-%dT16:00:00.000Z)\",
    \"location\": \"Home Office\",
    \"isAllDay\": false
  }" | jq .

curl -s -X POST "http://localhost:3001/api/events" \
  -H "Content-Type: application/json" \
  -H "x-user-id: $USER_ID" \
  -d "{
    \"title\": \"Meal Planning\",
    \"description\": \"Plan healthy meals for next week\",
    \"startTime\": \"$(date -u -d 'next sunday 10:00' +%Y-%m-%dT10:00:00.000Z)\",
    \"endTime\": \"$(date -u -d 'next sunday 11:00' +%Y-%m-%dT11:00:00.000Z)\",
    \"location\": \"Home\",
    \"isAllDay\": false
  }" | jq .

echo ""
echo "✅ Demo data created successfully!"
echo "- 6 Habits (one for each type)"
echo "- 3 Tasks"
echo "- 3 Calendar Events"
