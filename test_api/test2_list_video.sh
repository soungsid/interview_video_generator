#!/bin/bash

# InterviewVideoGenerator API Testing Script
# This script demonstrates all API endpoints

API_URL="http://localhost:8001/api"

echo "======================================"
echo "InterviewVideoGenerator API Tests"
echo "======================================"
echo ""


# Test 2: List All Videos
echo "2. Testing List All Videos (GET /api/videos)"
echo "---------------------------------------------"
curl -s "$API_URL/videos" | python3 -c "
import sys, json
videos = json.load(sys.stdin)
print(f\"Total videos: {len(videos)}\")
for i, v in enumerate(videos[:5], 1):
    print(f\"  {i}. {v['title']} (created: {v['created_at'][:10]})\")
if len(videos) > 5:
    print(f\"  ... and {len(videos) - 5} more\")
"
echo ""
echo ""

# Test 5: Test with custom model parameter
echo "5. Testing with Custom Model Parameter"
echo "---------------------------------------"
echo "Generating with model parameter (deepseek-chat)..."
curl -s -X POST "$API_URL/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "REST API Best Practices",
    "num_questions": 2,
    "model": "deepseek-chat"
  }' | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Video ID: {data['id']}\")
print(f\"Topic: {data['topic']}\")
print(f\"Number of dialogues: {len(data['dialogues'])}\")
"
echo ""
echo ""

echo "======================================"
echo "All tests completed successfully!"
echo "======================================"
echo ""
echo "You can access interactive API documentation at:"
echo "  - Swagger UI: http://localhost:8001/docs"
echo "  - ReDoc: http://localhost:8001/redoc"
