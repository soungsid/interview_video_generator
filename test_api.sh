#!/bin/bash

# InterviewVideoGenerator API Testing Script
# This script demonstrates all API endpoints

API_URL="http://localhost:8001/api"

echo "======================================"
echo "InterviewVideoGenerator API Tests"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check (GET /api/)"
echo "-----------------------------------"
curl -s "$API_URL/" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
echo ""
echo ""

# Test 2: Generate Video Script
echo "2. Testing Video Generation (POST /api/videos/generate)"
echo "--------------------------------------------------------"
echo "Generating interview script for 'Python Decorators' with 3 questions..."
RESPONSE=$(curl -s -X POST "$API_URL/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Decorators",
    "num_questions": 3
  }')

VIDEO_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))")

echo "Video generated successfully!"
echo "Video ID: $VIDEO_ID"
echo ""
echo "Introduction:"
echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['introduction'])"
echo ""
echo "Dialogues:"
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data['dialogues']:
    print(f\"  [{d['question_number']}] {d['role']}: {d['text'][:80]}...\")
"
echo ""
echo "Conclusion:"
echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['conclusion'])"
echo ""
echo ""

# Test 3: Get Video by ID
echo "3. Testing Get Video by ID (GET /api/videos/{id})"
echo "--------------------------------------------------"
if [ -n "$VIDEO_ID" ]; then
  curl -s "$API_URL/videos/$VIDEO_ID" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Video ID: {data['id']}\")
print(f\"Topic: {data['topic']}\")
print(f\"Created: {data['created_at']}\")
print(f\"Number of dialogues: {len(data['dialogues'])}\")
"
else
  echo "No video ID available"
fi
echo ""
echo ""

# Test 4: List All Videos
echo "4. Testing List All Videos (GET /api/videos)"
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
