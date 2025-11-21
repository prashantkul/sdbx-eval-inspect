# LangSmith Tracing Setup

LangSmith provides comprehensive observability for the autonomous agent evaluation, showing:
- **All LLM calls** with full inputs/outputs
- **Tool invocations** (bash commands, file operations, network requests)
- **Subagent spawning** and delegation
- **Token usage** per call
- **Full execution graph** showing agent reasoning flow

This is critical for understanding:
1. **What command triggered the password prompt**
2. **Whether the agent is spawning subagents**
3. **The agent's reasoning before taking actions**
4. **All intermediate tool calls and responses**

---

## Quick Setup (5 minutes)

### 1. Create LangSmith Account
- Go to https://smith.langchain.com
- Sign up (free account available)
- No credit card required for development

### 2. Generate API Key
- After login, click your profile → **Settings**
- Go to **API Keys** section
- Click **Create API Key**
- Copy the key (you won't see it again!)

### 3. Update `.env` File
```bash
# In sdbx-eval-fwk/.env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_key_here_abc123xyz
LANGCHAIN_PROJECT=phase4-autonomous-eval
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 4. Run Test
```bash
cd experiments/phase4-autonomous
python -u run_full_local_test.py
```

---

## What You'll See

### In Console
```
======================================================================
LANGSMITH TRACING SETUP
======================================================================
✓ LangSmith tracing enabled
  Project: phase4-autonomous-eval
  View traces at: https://smith.langchain.com
```

### In LangSmith UI (https://smith.langchain.com)

1. **Projects** → `phase4-autonomous-eval`
2. Each test run appears as a **Trace**
3. Click on a trace to see:

   **Execution Graph:**
   - Visual tree showing agent → tool → subagent flow
   - Time spent in each step
   - Token usage per LLM call

   **Tool Calls:**
   - **bash** calls with exact commands
   - **write_file** calls with paths and content
   - **task** calls showing subagent delegation
   - **Tool responses** showing output/errors

   **LLM Interactions:**
   - System prompts
   - User messages
   - Assistant responses
   - Tool call requests

---

## Critical for Investigation

For the **password prompt issue**, LangSmith will show:

```
Round 1 → Agent LLM Call
  ├─ System: "You are a security research assistant..."
  ├─ User: "Begin the security audit. Start by planning..."
  └─ Assistant: [response with tool calls]
      └─ Tool Call: bash
          └─ Command: "sudo systemctl list-units"  ← THE CULPRIT!
```

This lets you see:
- ✅ Exactly which bash command triggered sudo
- ✅ What the agent's reasoning was before the call
- ✅ Whether it tried other commands first
- ✅ If it spawned a subagent or did it directly

---

## Cost

LangSmith free tier includes:
- ✅ 5,000 traces/month (plenty for development)
- ✅ 7-day trace retention
- ✅ Full debugging features

For this evaluation:
- Each test run = 1 trace
- Can run ~100 tests easily within free tier

---

## Alternative: Local Logging

If you don't want to use LangSmith, the code still works without it.
You'll see detailed console output including:
- Agent responses
- Tool calls with arguments
- Token usage per round

But you WON'T get:
- ❌ Persistent traces
- ❌ Visual execution graph
- ❌ Subagent execution details
- ❌ Exact tool inputs/outputs in structured format

---

## Recommendation

**Enable LangSmith** for this investigation. It's the fastest way to:
1. See exactly what command triggered the password prompt
2. Understand the agent's decision-making process
3. Verify if subagents are being spawned
4. Debug token explosion issues

Total setup time: ~5 minutes
Value: Immediately see what's happening inside the agent
