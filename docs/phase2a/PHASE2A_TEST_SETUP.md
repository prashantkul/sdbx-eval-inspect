# Phase 2A Testing - Setup Required

## Current Status

**Docker**: ✅ Installed (v28.5.1)
**Docker Daemon**: ❌ Not running
**Secure MCP Server**: ❌ Not running

## Quick Setup (2 Minutes)

### Step 1: Start Docker

```bash
# On Mac: Open Docker Desktop
open -a Docker

# Wait ~30 seconds for Docker to start, then verify:
docker ps
```

### Step 2: Start Secure MCP Server

```bash
# Navigate to the MCP server repository
cd /path/to/llm-sdbx-escape-langgraph

# Start the secure MCP server
docker-compose up -d secure-mcp-server

# Verify it's healthy
curl http://localhost:8001/health
# Should return: {"status": "healthy"}
```

### Step 3: Run Phase 2A Test

```bash
# Navigate back to evaluation framework
cd /Users/prashantkulkarni/Documents/source-code/sdbx-eval-fwk

# Test docker-socket-exposed (easiest to test first)
conda run -n sdbx-eval-fwk python run_eval.py \
  --sandbox docker-socket-exposed \
  --mcp-server secure \
  --rounds 3
```

## What Each Prerequisite Does

### Docker Daemon
- Runs the containers for Phase 2A sandboxes
- Inspect uses Docker to create isolated environments
- Must be running for any Phase 2A test

### Secure MCP Server (Port 8001)
- Provides hardened tools (from Phase 1)
- Ensures we're testing environment security, not tool bugs
- Must be running for proper Phase 2 evaluation

## Alternative: Test Without MCP Server

If you want to test the Phase 2A sandbox infrastructure without the MCP server, you can use local tools (though they have Phase 1 vulnerabilities):

```bash
# This tests sandbox detection but uses vulnerable local tools
python run_eval.py --sandbox docker-socket-exposed --rounds 3
```

**Note**: This is not recommended for Phase 2 because local tools have `shell=True` (Phase 1 vulnerability).

## Once Setup is Complete

Run this command to execute your automated tests:
```bash
# I can run this for you once Docker and MCP server are started
```

Please let me know once you've:
1. Started Docker Desktop
2. Started the secure MCP server

Then I can proceed with automated testing!
