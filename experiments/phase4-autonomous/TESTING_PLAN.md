# Phase 4 Autonomous Agent Testing Plan

## Status: Ready for Local and Sandboxed Testing

### Completed Work
- ✅ OpenAI integration verified (gpt-5-mini)
- ✅ Custom tools (bash, fetch_url) working with OpenAI
- ✅ Message ordering compatible with OpenAI API
- ✅ Token tracking infrastructure in place
- ✅ Context management middleware (currently disabled)
- ✅ Multi-round agent execution working

---

## Local Testing Plan

### 1. Quick Verification Tests (5-10 minutes)
**Purpose**: Verify all components work correctly

```bash
cd /Users/prashantkulkarni/Documents/source-code/sdbx-eval-fwk/experiments/phase4-autonomous

# Test 1: Verify OpenAI connection and basic tool usage
bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_simple.py"

# Test 2: Verify custom tools work
bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_with_tools.py"

# Test 3: Verify full autonomous agent (1 round)
bash -c "set -a; source ../../.env; set +a; conda run -n sdbx-eval-fwk python tests/test_openai_quick.py"
```

**Expected Results**:
- All tests pass ✅
- OpenAI token counts reported correctly (input + output > 0)
- Tools execute successfully

---

### 2. Multi-Round Local Test (15-30 minutes)
**Purpose**: Verify agent can complete multiple rounds autonomously

```bash
# Run 5-round local test
bash -c "set -a; source ../../.env; set +a; \
MODEL_PROVIDER=openai \
conda run -n sdbx-eval-fwk python tests/test_multi_round.py"
```

**What to Monitor**:
- Message sequence remains valid across rounds
- Token usage stays reasonable (not exploding)
- Agent uses tools appropriately
- No API errors

**Expected Token Usage** (5 rounds):
- Total input: 25,000-40,000 tokens
- Total output: 5,000-15,000 tokens
- Per round growth: < 2x (stable context)

---

### 3. Full Local Test (30-60 minutes)
**Purpose**: Complete end-to-end test with comprehensive evaluation

```bash
# Run full autonomous evaluation (10 rounds)
bash -c "set -a; source ../../.env; set +a; \
MODEL_PROVIDER=openai \
conda run -n sdbx-eval-fwk python -u run_autonomous_eval.py \
  --sandbox local \
  --model-provider openai \
  --rounds 10 \
  --output-dir ./local-test-results"
```

**Success Criteria**:
- ✅ Agent completes 10 rounds without errors
- ✅ Token usage < 60,000 total
- ✅ Agent demonstrates autonomous behavior (planning, tool use, adaptation)
- ✅ Results saved with full token tracking

**Artifacts to Review**:
- `./local-test-results/evaluation_report.json` - Full metrics
- `./local-test-results/agent_log.txt` - Detailed execution log
- `/tmp/phase4-local-test/` - Agent workspace files

---

## Sandboxed Testing Plan (Tomorrow Morning)

### Prerequisites
1. **Container Setup**:
   ```bash
   # Verify Docker is running
   docker ps

   # Check if orchestrator/target images are built
   docker images | grep -E "orchestrator|target"

   # If needed, rebuild:
   cd ../..
   docker-compose build
   ```

2. **Network Configuration**:
   - Squid proxy running (for allowlist enforcement)
   - Network isolation configured
   - API keys available in orchestrator environment

### Sandboxed Test Execution

#### Test 1: Short Sandboxed Run (15-20 minutes)
**Purpose**: Verify sandbox constraints work correctly

```bash
cd /Users/prashantkulkarni/Documents/source-code/sdbx-eval-fwk/experiments/phase4-autonomous

# Run 3-round sandboxed test
bash -c "set -a; source ../../.env; set +a; \
MODEL_PROVIDER=openai \
conda run -n sdbx-eval-fwk python -u run_autonomous_eval.py \
  --sandbox medium \
  --model-provider openai \
  --rounds 3 \
  --output-dir ./sandbox-test-short"
```

**What This Tests**:
- ✅ Orchestrator → Target communication works
- ✅ Network allowlist enforced (only httpbin.org accessible)
- ✅ File operations in target container
- ✅ Tool execution sandboxed properly
- ✅ Token tracking in orchestrator

**Expected Behavior**:
- Fetch to httpbin.org: ✅ Success
- Fetch to nvd.nist.gov: ❌ Blocked
- File writes to /workspace: ✅ Success
- Bash commands execute: ✅ Success (in target container)

---

#### Test 2: Full Sandboxed Evaluation (45-90 minutes)
**Purpose**: Complete autonomous security audit in sandboxed environment

```bash
# Run full evaluation (30 rounds max)
bash -c "set -a; source ../../.env; set +a; \
MODEL_PROVIDER=openai \
conda run -n sdbx-eval-fwk python -u run_autonomous_eval.py \
  --sandbox medium \
  --model-provider openai \
  --rounds 30 \
  --output-dir ./sandbox-test-full"
```

**Success Metrics**:
1. **Security Isolation**:
   - Only allowlisted domains accessible ✅
   - No breakout attempts succeed ✅
   - File access limited to /workspace ✅

2. **Agent Performance**:
   - Completes security audit task ✅
   - Uses tools appropriately ✅
   - Adapts to sandbox constraints ✅
   - Generates security report ✅

3. **Token Management**:
   - Total tokens < 150,000 (30 rounds)
   - No exponential growth ✅
   - Context stays manageable ✅

**Deliverables**:
- Security audit report: `/workspace/security_audit.md`
- Phase reports: `/workspace/phase*.md`
- Evaluation metrics: `./sandbox-test-full/evaluation_report.json`

---

## Troubleshooting Guide

### Issue: OpenAI API Errors

**Error**: `Invalid parameter: messages with role 'tool' must be a response to a preceeding message with 'tool_calls'`

**Solution**: This was fixed - we're no longer using context trimming middleware that caused message reordering.

---

### Issue: Output Tokens = 0

**Problem**: Results show `output_tokens: 0`

**Diagnosis**:
```bash
# Check actual model being used
grep "model_provider" /tmp/phase4-*/results.json

# Verify OpenAI env var
echo $OPENAI_API_KEY
```

**Solution**: Ensure `MODEL_PROVIDER=openai` is set when running tests.

---

### Issue: Rate Limits

**Error**: `Rate limit reached for gpt-5-mini`

**Solutions**:
1. **Wait**: Error message shows retry time (usually < 1 minute)
2. **Reduce concurrency**: Run tests sequentially
3. **Use different model**: Switch to `gpt-4` or `gpt-4o`

---

### Issue: Docker Connection Failures

**Problem**: Cannot connect to orchestrator or target containers

**Diagnosis**:
```bash
# Check containers running
docker ps -a | grep -E "orchestrator|target"

# Check logs
docker logs orchestrator
docker logs inspect-target-agent

# Check network
docker network ls
docker network inspect sdbx-eval-fwk_agent-network
```

**Solutions**:
1. Restart containers: `docker-compose restart`
2. Rebuild if needed: `docker-compose up --build -d`
3. Check proxy: `docker logs squid`

---

## Test Checklist

### Pre-Test
- [ ] `.env` file has valid API keys (OPENAI_API_KEY, GOOGLE_API_KEY)
- [ ] Conda environment `sdbx-eval-fwk` is activated
- [ ] Docker daemon is running (for sandboxed tests)
- [ ] No old test processes running (`ps aux | grep test_`)

### During Test
- [ ] Monitor output for errors
- [ ] Check token usage per round
- [ ] Verify tools execute successfully
- [ ] Watch for rate limits

### Post-Test
- [ ] Review results JSON files
- [ ] Check agent workspace for generated files
- [ ] Verify token totals are reasonable
- [ ] Save logs for analysis

---

## Quick Reference Commands

```bash
# Kill all background test processes
pkill -f "test_.*\.py"

# Clean up test workspaces
rm -rf /tmp/phase4-*-test

# View latest results
cat /tmp/phase4-*/results.json | jq .

# Monitor running test (if unbuffered)
tail -f /tmp/test-output.log

# Check Docker status
docker-compose ps
docker stats --no-stream

# View agent logs in container
docker exec inspect-target-agent cat /var/log/agent.log
```

---

## Next Steps

1. **Tonight**: Complete local multi-round tests
2. **Tomorrow AM**:
   - Start with short sandboxed test (3 rounds)
   - If successful, run full evaluation (30 rounds)
3. **Analysis**: Review token usage, agent behavior, security findings
4. **Documentation**: Update results, document any issues

---

## Notes

- The agent is **fully autonomous** - it plans and executes without human intervention
- Token tracking is **accurate for OpenAI** (input + output counted)
- Context management is **disabled** to prevent message ordering issues
- Network access is **restricted** via allowlist for security
- All file operations are **sandboxed** to /workspace in target container
