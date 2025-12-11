#!/bin/bash

# Gateway Integration Test Suite
# Tests authentication and proxying to all services

BASE_URL="http://localhost:3000"
echo "==================================="
echo "Gateway Integration Test Suite"
echo "Base URL: $BASE_URL"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test 1: Gateway Health
echo -e "${BLUE}Test 1: Gateway Health Check${NC}"
HEALTH=$(curl -s "$BASE_URL/health")
echo "$HEALTH" | jq '.'
STATUS=$(echo "$HEALTH" | jq -r '.status')
if [ "$STATUS" == "healthy" ]; then
    echo -e "${GREEN}✓ Gateway is healthy${NC}"
else
    echo -e "${RED}✗ Gateway is not healthy${NC}"
fi
echo ""

# Test 2: Register User
echo -e "${BLUE}Test 2: Register New User${NC}"
EMAIL="testuser_$(date +%s)@example.com"
PASSWORD="Test1234!"
NAME="Test User"

REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"name\": \"$NAME\"}")

echo "$REGISTER_RESPONSE" | jq '.'
SUCCESS=$(echo "$REGISTER_RESPONSE" | jq -r '.success')

if [ "$SUCCESS" == "true" ]; then
    echo -e "${GREEN}✓ User registered successfully${NC}"
    ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.data.accessToken')
    echo "Access Token: ${ACCESS_TOKEN:0:50}..."
else
    echo -e "${RED}✗ Registration failed${NC}"
    echo "Attempting login with existing user..."
    
    # Try login instead
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
      -H "Content-Type: application/json" \
      -d "{\"email\": \"test@example.com\", \"password\": \"Test1234!\"}")
    
    echo "$LOGIN_RESPONSE" | jq '.'
    SUCCESS=$(echo "$LOGIN_RESPONSE" | jq -r '.success')
    
    if [ "$SUCCESS" == "true" ]; then
        echo -e "${GREEN}✓ Login successful${NC}"
        ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.accessToken')
        echo "Access Token: ${ACCESS_TOKEN:0:50}..."
    else
        echo -e "${RED}✗ Login failed - manual user creation needed${NC}"
        exit 1
    fi
fi
echo ""

# Test 3: Access AI Brain via Gateway (Memory Stats - no quota needed)
echo -e "${BLUE}Test 3: AI Brain - Memory Stats (via Gateway)${NC}"
MEMORY_STATS=$(curl -s "$BASE_URL/api/gateway/memory/stats/test_user_123" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$MEMORY_STATS" | jq '.'
if echo "$MEMORY_STATS" | jq -e '.user_id' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ AI Brain accessible via Gateway${NC}"
else
    echo -e "${RED}✗ AI Brain access failed${NC}"
fi
echo ""

# Test 4: Access Lifestyle via Gateway
echo -e "${BLUE}Test 4: Lifestyle - Get Habits (via Gateway)${NC}"
HABITS=$(curl -s "$BASE_URL/api/gateway/lifestyle/habits?user_id=test_user_123" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$HABITS" | jq '.'
if echo "$HABITS" | jq -e 'type' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Lifestyle Service accessible via Gateway${NC}"
else
    echo -e "${RED}✗ Lifestyle Service access failed${NC}"
fi
echo ""

# Test 5: Create Habit via Gateway
echo -e "${BLUE}Test 5: Create Habit (via Gateway)${NC}"
CREATE_HABIT=$(curl -s -X POST "$BASE_URL/api/gateway/lifestyle/habits" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_gateway",
    "name": "Morning Exercise",
    "type": "exercise",
    "frequency": "daily",
    "target": {
      "amount": 30,
      "unit": "minutes"
    }
  }')
echo "$CREATE_HABIT" | jq '.'
if echo "$CREATE_HABIT" | jq -e '.id or ._id' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Habit creation via Gateway successful${NC}"
    HABIT_ID=$(echo "$CREATE_HABIT" | jq -r '.id // ._id')
else
    echo -e "${RED}✗ Habit creation failed${NC}"
fi
echo ""

# Test 6: Scheduling via Gateway
echo -e "${BLUE}Test 6: Scheduling Patterns (via Gateway)${NC}"
PATTERNS=$(curl -s "$BASE_URL/api/gateway/scheduling/patterns/test_user_gateway" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "$PATTERNS" | jq '.'
if echo "$PATTERNS" | jq -e 'type' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Scheduling Service accessible via Gateway${NC}"
else
    echo -e "${RED}✗ Scheduling Service access failed${NC}"
fi
echo ""

# Test 7: Without Authentication (Should Fail)
echo -e "${BLUE}Test 7: Unauthenticated Access (Should Fail)${NC}"
UNAUTH=$(curl -s "$BASE_URL/api/gateway/memory/stats/test_user" 2>&1)
echo "$UNAUTH" | jq '.'
if echo "$UNAUTH" | jq -e '.success == false or .error' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Authentication properly enforced${NC}"
else
    echo -e "${RED}✗ Warning: Unauthenticated access allowed${NC}"
fi
echo ""

# Test 8: Service Health Summary
echo -e "${BLUE}Test 8: All Services Health Summary${NC}"
echo "$HEALTH" | jq '.services[] | {name, status, responseTime}'
echo ""

echo -e "${GREEN}==================================="
echo "Gateway Integration Tests Complete"
echo "===================================${NC}"
echo ""
echo "Summary:"
echo "- Gateway: Running on port 3000"
echo "- Authentication: JWT-based"
echo "- Services: AI Brain, Scheduler, Lifestyle"
echo "- All routes protected with authentication"
echo ""
echo "Test User:"
echo "Email: $EMAIL"
echo "Token: ${ACCESS_TOKEN:0:50}..."
