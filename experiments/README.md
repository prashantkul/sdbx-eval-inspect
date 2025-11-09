# Experiments Directory

This directory contains organized experiments for different phases of the evaluation framework.

## Structure

```
experiments/
├── phase1/              # Phase 1: MCP Tool Security (future - if needed)
├── phase2a/             # Phase 2A: Docker Misconfigurations (CURRENT)
│   ├── docker-socket-exposed/
│   ├── docker-cap-sys-admin/
│   ├── docker-privileged/
│   └── docker-pid-host/
└── phase2b/             # Phase 2B: Native Sandbox Tools (future)
```

## Phase 2A: Docker Misconfigurations

Each subdirectory contains:
- `compose.yaml` - Docker Compose configuration with intentional misconfiguration
- `README.md` - Description of the misconfiguration and expected behavior
- Test results (generated during evaluation)

## Purpose

This organization allows us to:
1. **Track experiments** - Each phase has its own folder
2. **Isolate configurations** - No confusion between different sandbox types
3. **Document findings** - READMEs explain each misconfiguration
4. **Reproduce results** - Clear structure for future testing

## Usage

Experiments are referenced by the framework automatically when you specify a sandbox type:

```bash
python run_eval.py --sandbox docker-socket-exposed --mcp-server secure --rounds 3
```

Inspect will look for the compose file in the corresponding experiment directory.
