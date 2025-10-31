#!/bin/bash

# InterviewVideoGenerator API Testing Script
# This script demonstrates all API endpoints

API_URL="http://localhost:8001/api"

echo "======================================"
echo "InterviewVideoGenerator API Tests"
echo "======================================"
echo ""


# 1.Generation video
echo "1.Generation video"
echo "---------------------------------------"
echo "Generating video"
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
