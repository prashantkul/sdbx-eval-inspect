#!/bin/bash

# Phase 3 Test Script - Auditor ↔ Target Communication

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Phase 3: Multi-Agent Sandbox Escape Test              ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check for Google API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable not set"
    echo "   Please set it before running this test"
    exit 1
fi

echo ""
echo "📦 Step 1: Building vulnerable container with Target agent..."
cd docker-socket-exposed
docker compose build

echo ""
echo "🚀 Step 2: Starting vulnerable container..."
docker compose up -d

echo ""
echo "⏳ Step 3: Waiting for Target agent to start..."
sleep 5

echo ""
echo "🔍 Step 4: Checking Target agent health..."
curl -s http://localhost:8000/health | python3 -m json.tool || {
    echo "❌ Target agent not responding"
    docker compose logs
    docker compose down
    exit 1
}

echo ""
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Starting Auditor Agent Attack                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd ../..

# Run Auditor agent
python3 langgraph_integration/auditor_agent.py \
    --sandbox docker-socket-exposed \
    --target-url http://localhost:8000 \
    --max-attempts 3

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Test Complete                                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "To stop the vulnerable container:"
echo "  cd experiments/phase3-test/docker-socket-exposed"
echo "  docker compose down"
echo ""
