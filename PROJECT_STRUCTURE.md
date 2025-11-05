# Project Structure

## Clean, Organized Directory Layout

```
sdbx-eval-fwk/
│
├── 📄 CORE DOCUMENTATION
│   ├── README.md                      # Complete guide
│   ├── QUICKSTART.md                  # 5-minute start
│   ├── PROJECT_SUMMARY.md             # Technical overview
│   └── PROJECT_STRUCTURE.md           # This file
│
├── ⚙️ CONFIGURATION
│   ├── .env.example                   # Environment template
│   └── config/
│       ├── __init__.py
│       ├── base_config.py            # Base settings
│       ├── agent_config.py           # Agent configurations
│       └── sandbox_config.py         # Sandbox settings
│
├── 🎯 INSPECT INTEGRATION (Primary Implementation)
│   └── inspect_integration/
│       ├── __init__.py               # Package exports
│       ├── tasks_native.py           # Task definitions
│       │
│       ├── agents/                   # Three separate agent files
│       │   ├── __init__.py
│       │   ├── auditor_agent.py     # Red team agent (no tools)
│       │   ├── target_agent.py      # Sandboxed agent (with tools)
│       │   └── judge_agent.py       # Evaluator agent (no tools)
│       │
│       ├── prompts/                  # Agent-specific prompts
│       │   ├── __init__.py
│       │   ├── auditor_prompts.py   # Red team prompts
│       │   ├── target_prompts.py    # Sandboxed agent prompts
│       │   └── judge_prompts.py     # Evaluator prompts
│       │
│       ├── solvers/                  # Solver implementations
│       │   ├── __init__.py
│       │   ├── coordinated_solver.py # Main solver logic (3-agent orchestration)
│       │   └── tools.py             # Tool definitions & MCP integration
│       │
│       └── scorers/                  # Scoring functions
│           ├── __init__.py
│           ├── scorers.py           # 6 comprehensive scorers
│           └── analysis.py          # Analysis utilities
│
├── 🔌 MCP INTEGRATION
│   └── mcp_integration/
│       ├── README.md                 # MCP server documentation
│       ├── client.py                 # MCP client implementation
│       └── servers.py                # Server configurations (vulnerable, secure, baseline)
│
├── 📚 ENTRY POINT
│   └── run_eval.py                   # Main CLI entry point
│
├── 📦 DEPENDENCIES
│   └── requirements.txt              # Python dependencies
│
└── 📊 OUTPUT DIRECTORIES (Created at runtime)
    ├── logs/                          # Evaluation logs
    └── results/                       # Results JSON files
```

## File Count

- **Total Files**: ~25 Python files + 4 documentation files
- **Inspect Integration**: 15 files
  - Agents: 3 files (auditor, target, judge)
  - Prompts: 3 files (one per agent)
  - Solvers: 2 files (solver + tools)
  - Scorers: 2 files (scorers + analysis)
  - Tasks: 1 file
- **MCP Integration**: 3 files (client, servers, README)
- **Configuration**: 4 files
- **Documentation**: 4 files

## Key Files

### Entry Points

| File | Purpose | Usage |
|------|---------|-------|
| `run_eval.py` | Simple CLI entry | `python run_eval.py --rounds 3` |
| `inspect_integration/tasks_native.py` | Inspect tasks | `inspect eval ...@sandbox_escape_native` |

### Core Implementation (Inspect-Native)

| File | Lines | Purpose |
|------|-------|---------|
| **Agents** | | **Three separate agent files** |
| `agents/auditor_agent.py` | ~60 | Red team agent (NO tools) |
| `agents/target_agent.py` | ~80 | Sandboxed agent (WITH tools) |
| `agents/judge_agent.py` | ~60 | Evaluator agent (NO tools) |
| **Prompts** | | **Agent-specific prompts** |
| `prompts/auditor_prompts.py` | ~83 | Red team agent prompts |
| `prompts/target_prompts.py` | ~50 | Sandboxed agent prompts |
| `prompts/judge_prompts.py` | ~65 | Evaluator prompts |
| **Solvers** | | **Solver implementations** |
| `solvers/coordinated_solver.py` | ~152 | Main 3-agent orchestration |
| `solvers/tools.py` | ~150 | Tool definitions & MCP |
| **Scorers** | | **Evaluation metrics** |
| `scorers/scorers.py` | ~350 | 6 comprehensive scorers |
| `scorers/analysis.py` | ~260 | Analysis utilities |
| **Tasks** | | **Task definitions** |
| `tasks_native.py` | ~100 | Inspect task definitions |

### Configuration

| File | Purpose |
|------|---------|
| `base_config.py` | LLM, logging, Inspect settings |
| `agent_config.py` | Auditor, Target, Judge configs |
| `sandbox_config.py` | Docker, gVisor, Firecracker configs |

## Three-Agent Architecture

This implementation follows Petri's three-agent pattern:

### 1. Auditor Agent (Red Team)
- **File**: `inspect_integration/agents/auditor_agent.py`
- **Prompts**: `inspect_integration/prompts/auditor_prompts.py`
- **Tools**: NONE (pure reasoning)
- **Role**: Crafts instructions to get target to escape sandbox

### 2. Target Agent (Sandboxed Subject)
- **File**: `inspect_integration/agents/target_agent.py`
- **Prompts**: `inspect_integration/prompts/target_prompts.py`
- **Tools**: Shell, Python, file operations, or MCP server
- **Role**: Executes auditor's instructions within sandbox

### 3. Judge Agent (Evaluator)
- **File**: `inspect_integration/agents/judge_agent.py`
- **Prompts**: `inspect_integration/prompts/judge_prompts.py`
- **Tools**: NONE (pure reasoning)
- **Role**: Evaluates success and scores attempts

## Usage Patterns

### 1. Command Line (Recommended)

```bash
python run_eval.py --sandbox docker --rounds 5
```

**Files involved:**
- `run_eval.py`
- `inspect_integration/tasks_native.py`
- `inspect_integration/solvers/coordinated_solver.py`
- `inspect_integration/agents/auditor_agent.py`
- `inspect_integration/agents/target_agent.py`
- Configuration files

### 2. Python API

```python
from inspect_ai import eval
from inspect_integration.tasks_native import sandbox_escape_native

results = eval(
    sandbox_escape_native(sandbox_type="docker"),
    model="google/gemini-2.5-pro"
)
```

**Files involved:**
- `inspect_integration/tasks_native.py`
- `inspect_integration/solvers/coordinated_solver.py`
- `inspect_integration/scorers/scorers.py`
- `inspect_integration/agents/*.py`

### 3. Inspect CLI

```bash
inspect eval inspect_integration/tasks_native.py@sandbox_escape_native \
  --model google/gemini-2.5-pro
```

**Files involved:**
- Same as Python API

## Dependencies Between Files

```
run_eval.py
    └─> inspect_integration/tasks_native.py
            └─> solvers/coordinated_solver.py
                    ├─> prompts/auditor_prompts.py
                    ├─> prompts/target_prompts.py
                    ├─> solvers/tools.py
                    └─> scorers/analysis.py
```

## What Each Directory Does

| Directory | Purpose | When to Use |
|-----------|---------|-------------|
| `inspect_integration/` | Inspect-native implementation | Default choice, production |
| `inspect_integration/agents/` | Three agent implementations | Customize agent behavior |
| `inspect_integration/prompts/` | Agent-specific prompts | Customize prompts |
| `inspect_integration/solvers/` | Orchestration logic | Customize evaluation flow |
| `inspect_integration/scorers/` | Scoring & analysis | Customize metrics |
| `config/` | Settings and configuration | Customize behavior |
| `mcp_integration/` | MCP server integration | Test different tool security |
| `logs/` | Evaluation logs | Review results |
| `results/` | JSON output | Analysis, reporting |

## Removed Files (Cleaned Up)

The following were removed during cleanup:

- ❌ `agents/` directory (LangGraph implementation)
- ❌ `examples/` directory
- ❌ `inspect_integration/prompts/agent_prompts.py` (redundant consolidation)
- ❌ Old naming: attacker → auditor, evaluator → judge

## Clean Architecture Benefits

1. **Single Entry Point**: Only `run_eval.py` in root
2. **Clear Separation**: Three agents in separate files
3. **No Duplicates**: Each file has a single purpose
4. **Easy Navigation**: Logical directory structure
5. **Minimal Dependencies**: Clean import chains
6. **Petri-Inspired**: Follows proven three-agent pattern

## Coordinated Solver Flow

The main orchestration happens in `solvers/coordinated_solver.py`:

```python
for round in range(max_rounds):
    # 1. Auditor turn (no tools)
    state.messages = [
        ChatMessageSystem(AUDITOR_PROMPT),
        ChatMessageUser("Generate attack instruction")
    ]
    state = await generate(state)  # No tools
    auditor_instruction = state.output.completion

    # 2. Target turn (with tools)
    state.messages = [
        ChatMessageSystem(TARGET_PROMPT),
        ChatMessageUser(f"Execute: {auditor_instruction}")
    ]
    state = await generate(state, tools=target_tools)  # With tools
    target_output = state.output.completion

    # 3. Check for escape
    if escape_detected(target_output):
        break

# 4. Score results
sophistication = calculate_sophistication_score(attack_chain)
stealth = calculate_stealth_score(attack_chain)
violations = classify_safety_violations(attack_chain)
```

## Next Steps

To extend the framework:

1. **Add custom prompts**: Edit files in `inspect_integration/prompts/`
2. **Add new tools**: Extend `inspect_integration/solvers/tools.py`
3. **Add scorers**: Extend `inspect_integration/scorers/scorers.py`
4. **Add sandboxes**: Extend `config/sandbox_config.py`
5. **Customize agents**: Edit files in `inspect_integration/agents/`
