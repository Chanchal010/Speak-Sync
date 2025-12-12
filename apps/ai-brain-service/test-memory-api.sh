#!/bin/bash

# Test Script for Vector Memory System
# Tests all memory management and semantic search endpoints

BASE_URL="http://localhost:8000"
USER_ID="test_user_$(date +%s)"
SESSION_ID="session_$(date +%s)"

echo "==================================="
echo "Vector Memory System Test Suite"
echo "==================================="
echo ""
echo "Test User: $USER_ID"
echo "Session: $SESSION_ID"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Memory Service Health Check${NC}"
curl -s "$BASE_URL/api/memory/health" | jq '.'
echo ""
echo ""

# Test 2: Store Conversation
echo -e "${BLUE}Test 2: Store Conversation with Embedding${NC}"
curl -s -X POST "$BASE_URL/api/memory/store-conversation" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"session_id\": \"$SESSION_ID\",
    \"conversation_text\": \"I really love running in the morning. It helps me clear my mind and start the day energized.\",
    \"metadata\": {\"topic\": \"exercise\", \"sentiment\": \"positive\"}
  }" | jq '.'
echo ""
echo ""

# Store another conversation
echo -e "${BLUE}Test 2b: Store Another Conversation${NC}"
curl -s -X POST "$BASE_URL/api/memory/store-conversation" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"session_id\": \"$SESSION_ID\",
    \"conversation_text\": \"I've been trying to wake up at 6 AM every day, but I keep hitting snooze. Need better discipline.\",
    \"metadata\": {\"topic\": \"habits\", \"sentiment\": \"concerned\"}
  }" | jq '.'
echo ""
echo ""

# Test 3: Store User Context
echo -e "${BLUE}Test 3: Store User Context (Preference)${NC}"
curl -s -X POST "$BASE_URL/api/memory/store-context" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"context_type\": \"preference\",
    \"context_key\": \"exercise_time\",
    \"context_value\": \"Prefers morning exercise, specifically running. Feels it improves mental clarity.\",
    \"importance\": 0.8
  }" | jq '.'
echo ""
echo ""

# Store another context
echo -e "${BLUE}Test 3b: Store User Context (Goal)${NC}"
curl -s -X POST "$BASE_URL/api/memory/store-context" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"context_type\": \"goal\",
    \"context_key\": \"wake_time\",
    \"context_value\": \"User wants to wake up at 6 AM consistently. Currently struggling with discipline.\",
    \"importance\": 0.9
  }" | jq '.'
echo ""
echo ""

# Test 4: Recall Similar Conversations
echo -e "${BLUE}Test 4: Semantic Search - Recall Similar Conversations${NC}"
curl -s -X POST "$BASE_URL/api/memory/recall-conversations" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"query\": \"morning exercise routine\",
    \"limit\": 5,
    \"similarity_threshold\": 0.6
  }" | jq '.'
echo ""
echo ""

# Test 5: Retrieve Relevant Context
echo -e "${BLUE}Test 5: Retrieve Relevant Context${NC}"
curl -s -X POST "$BASE_URL/api/memory/retrieve-context" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"query\": \"help me build better morning habits\",
    \"limit\": 3
  }" | jq '.'
echo ""
echo ""

# Test 6: Get Contextual Summary
echo -e "${BLUE}Test 6: Get Contextual Summary${NC}"
curl -s -X POST "$BASE_URL/api/memory/contextual-summary" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"current_query\": \"What are my morning routine goals?\"
  }" | jq '.'
echo ""
echo ""

# Test 7: Get Conversation History
echo -e "${BLUE}Test 7: Get Conversation History${NC}"
curl -s -X POST "$BASE_URL/api/memory/conversation-history" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"session_id\": \"$SESSION_ID\",
    \"limit\": 10
  }" | jq '.'
echo ""
echo ""

# Test 8: Find Related Contexts
echo -e "${BLUE}Test 8: Find Related Contexts${NC}"
curl -s -X POST "$BASE_URL/api/memory/find-related" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"context_value\": \"morning exercise habits\",
    \"limit\": 5
  }" | jq '.'
echo ""
echo ""

# Test 9: Get Memory Statistics
echo -e "${BLUE}Test 9: Get Memory Statistics${NC}"
curl -s "$BASE_URL/api/memory/stats/$USER_ID" | jq '.'
echo ""
echo ""

# Test 10: Batch Store Conversations
echo -e "${BLUE}Test 10: Batch Store Conversations${NC}"
curl -s -X POST "$BASE_URL/api/memory/batch-store" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"session_id\": \"$SESSION_ID\",
    \"conversations\": [
      {
        \"text\": \"I started reading for 30 minutes before bed and it's been really helpful for sleep.\",
        \"metadata\": {\"topic\": \"sleep\"}
      },
      {
        \"text\": \"Need to drink more water throughout the day. Currently only having 3-4 glasses.\",
        \"metadata\": {\"topic\": \"hydration\"}
      },
      {
        \"text\": \"My productivity is highest between 9 AM and 12 PM. Should schedule important tasks then.\",
        \"metadata\": {\"topic\": \"productivity\"}
      }
    ]
  }" | jq '.'
echo ""
echo ""

# Test 11: Extract Contexts from Conversation
echo -e "${BLUE}Test 11: AI-Powered Context Extraction${NC}"
curl -s -X POST "$BASE_URL/api/memory/extract-contexts" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"conversation_text\": \"Hi, I'm Alex from San Francisco. I work as a software engineer and I'm passionate about building healthy habits. I love hiking on weekends and I'm trying to learn Spanish. My main goal this year is to run a marathon.\",
    \"context_hints\": [\"personal facts\", \"preferences\", \"goals\"]
  }" | jq '.'
echo ""
echo ""

# Test 12: Update Context Importance
echo -e "${BLUE}Test 12: Update Context Importance${NC}"
echo "(Using context_id=1 as example - adjust if needed)"
curl -s -X POST "$BASE_URL/api/memory/update-importance" \
  -H "Content-Type: application/json" \
  -d "{
    \"context_id\": 1,
    \"new_importance\": 0.95
  }" | jq '.'
echo ""
echo ""

# Test 13: Final Recall Test (after all data stored)
echo -e "${BLUE}Test 13: Final Semantic Search (All Topics)${NC}"
curl -s -X POST "$BASE_URL/api/memory/recall-conversations" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"query\": \"healthy lifestyle habits and routines\",
    \"limit\": 10,
    \"similarity_threshold\": 0.5
  }" | jq '.'
echo ""
echo ""

# Test 14: Cleanup (optional - commented out by default)
echo -e "${YELLOW}Test 14: Cleanup Old Memories (SKIPPED - uncomment to test)${NC}"
# Uncomment below to test cleanup:
# curl -s -X POST "$BASE_URL/api/memory/cleanup-memories" \
#   -H "Content-Type: application/json" \
#   -d "{
#     \"user_id\": \"$USER_ID\",
#     \"days_old\": 0
#   }" | jq '.'
echo "Cleanup test skipped (to preserve test data)"
echo ""
echo ""

echo -e "${GREEN}==================================="
echo "All Tests Completed!"
echo "===================================${NC}"
echo ""
echo "Summary:"
echo "- Stored multiple conversations with embeddings"
echo "- Stored user contexts (preferences, goals)"
echo "- Performed semantic searches"
echo "- Retrieved relevant contexts"
echo "- Batch operations tested"
echo "- AI context extraction tested"
echo ""
echo "Test User: $USER_ID"
echo "Check logs for any errors"
