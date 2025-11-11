# Phase 2B: Ubuntu VM Setup Guide (Option C - Native Execution)

## Decision: Why Option C?

**Option C (Run Everything on Ubuntu)** is the correct choice for Phase 2B because:

✅ **True Native Testing**
- nsjail/bubblewrap/firejail run directly on Linux kernel
- No Docker abstraction layer
- Real Linux namespaces, capabilities, seccomp

✅ **Accurate Misconfiguration Testing**
- Testing actual nsjail configs, not Docker+nsjail
- Native process execution
- Authentic sandbox behavior

✅ **Real-World Scenario**
- How these tools are actually deployed
- Production-like environment
- Direct kernel interactions

❌ **Option A (Docker on Ubuntu) is WRONG** because:
- Tests Docker wrapping native tools
- Docker's security masks native tool behavior
- Not representative of real deployments

## Architecture (Option C)

```
┌─────────────────────────────────────────────────────────┐
│ Mac (Development Machine)                               │
│ ├─ VS Code with Remote SSH extension                   │
│ ├─ Git operations                                       │
│ ├─ Terminal access to Ubuntu VM                        │
│ └─ Port forwarding for MCP server                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ SSH (VS Code Remote / Terminal)
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Ubuntu VM (VMware Fusion) - Everything Runs Here       │
│                                                          │
│ ~/sdbx-eval-fwk/  (Git repo synced)                    │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Python Environment                                 │  │
│ │ ├─ conda env: sdbx-eval-fwk                       │  │
│ │ ├─ Inspect framework                              │  │
│ │ ├─ Dependencies (requests, etc.)                  │  │
│ │ └─ Gemini API keys (.env)                         │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Inspect Evaluation Runner                          │  │
│ │ ├─ Auditor (Gemini API)                           │  │
│ │ ├─ Target (Gemini API)                            │  │
│ │ └─ Judge (Gemini API)                             │  │
│ └────────────────────────────────────────────────────┘  │
│            │                                             │
│            │ Direct subprocess.run()                     │
│            │ NO Docker wrapper!                          │
│            ▼                                             │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Native Linux Sandboxes                             │  │
│ │ ├─ /usr/local/bin/nsjail                          │  │
│ │ ├─ /usr/bin/bwrap (bubblewrap)                    │  │
│ │ └─ /usr/bin/firejail                              │  │
│ │                                                    │  │
│ │ Commands execute in TRUE native sandboxes:        │  │
│ │ nsjail --config /path/to/config.cfg -- /bin/bash  │  │
│ └────────────────────────────────────────────────────┘  │
│                                                          │
│ ┌────────────────────────────────────────────────────┐  │
│ │ MCP Server (from llm-sdbx-escape-langgraph)       │  │
│ │ ├─ Runs on Ubuntu VM                              │  │
│ │ ├─ Port 8001 (secure server)                      │  │
│ │ └─ Accessible from Mac via port forward           │  │
│ └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step Setup

### Step 1: Ubuntu VM Installation

1. **Download Ubuntu Server 22.04 LTS**
   ```bash
   # From Mac
   curl -O https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso
   ```

2. **Create VM in VMware Fusion**
   - Memory: 4GB minimum, 8GB recommended
   - CPUs: 2 cores minimum, 4 recommended
   - Disk: 40GB minimum
   - Network: NAT or Bridged (for SSH access)

3. **Ubuntu Installation Options**
   - Install OpenSSH server: **YES**
   - Username: `ubuntu` (or your preference)
   - Enable password authentication initially
   - Install basic utilities

### Step 2: Initial Ubuntu Configuration

```bash
# SSH into Ubuntu VM from Mac
ssh ubuntu@<ubuntu-vm-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install essential development tools
sudo apt install -y \
  build-essential \
  git \
  curl \
  wget \
  vim \
  htop \
  net-tools

# Install Python 3.11
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Step 3: Install Native Sandbox Tools

```bash
# 1. Install nsjail
sudo apt install -y \
  autoconf bison flex gcc g++ git \
  libprotobuf-dev libnl-route-3-dev libtool \
  make pkg-config protobuf-compiler

git clone https://github.com/google/nsjail.git
cd nsjail
make
sudo make install
nsjail --version  # Verify installation

# 2. Install bubblewrap
sudo apt install -y bubblewrap
bwrap --version

# 3. Install firejail
sudo apt install -y firejail
firejail --version

# 4. Install utilities for testing
sudo apt install -y \
  libcap2-bin \  # capsh for capability checking
  procps \       # ps, top
  util-linux     # mount, fdisk, etc.
```

### Step 4: Set Up Project Environment

```bash
# Clone your repository
cd ~
git clone https://github.com/prashantkul/sdbx-eval-inspect.git sdbx-eval-fwk
cd sdbx-eval-fwk

# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
~/miniconda3/bin/conda init bash
source ~/.bashrc

# Create conda environment
conda create -n sdbx-eval-fwk python=3.11 -y
conda activate sdbx-eval-fwk

# Install Inspect framework
pip install inspect-ai

# Install project dependencies
pip install -r requirements.txt  # If you have one
# Or install manually:
pip install requests python-dotenv
```

### Step 5: Configure Environment Variables

```bash
# Copy and edit .env file
cd ~/sdbx-eval-fwk
cp .env.example .env
vim .env

# Add your Gemini API key:
# GOOGLE_API_KEY=your_key_here
# AUDITOR_MODEL=gemini-2.5-pro
# TARGET_MODEL=gemini-2.5-flash
# JUDGE_MODEL=gemini-2.5-pro
```

### Step 6: Set Up MCP Server (Optional but Recommended)

```bash
# Clone MCP server repo
cd ~
git clone https://github.com/prashantkul/llm-sdbx-escape-langgraph.git
cd llm-sdbx-escape-langgraph

# Install Docker (for MCP server)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker  # Or logout/login

# Start secure MCP server
docker-compose up -d secure-mcp-server

# Verify it's running
curl http://localhost:8001/
docker-compose ps
```

### Step 7: Configure VS Code Remote (Mac)

On your Mac:

1. **Install VS Code Extension**
   - Install "Remote - SSH" extension

2. **Configure SSH**
   ```bash
   # On Mac, edit ~/.ssh/config
   Host ubuntu-vm
       HostName <ubuntu-vm-ip>
       User ubuntu
       Port 22
       IdentityFile ~/.ssh/id_rsa  # If using SSH keys
   ```

3. **Connect to VM**
   - CMD+Shift+P → "Remote-SSH: Connect to Host"
   - Select "ubuntu-vm"
   - Open folder: `/home/ubuntu/sdbx-eval-fwk`

4. **Install Python Extension on Remote**
   - Install "Python" extension on Ubuntu VM
   - Select interpreter: `sdbx-eval-fwk` conda env

### Step 8: Verify Setup

On Ubuntu VM:

```bash
# Activate environment
conda activate sdbx-eval-fwk

# Test nsjail
nsjail --help

# Test bubblewrap
bwrap --version

# Test firejail
firejail --version

# Test Inspect installation
python -c "import inspect_ai; print(inspect_ai.__version__)"

# Test Gemini API
export GOOGLE_API_KEY=your_key
python -c "from inspect_ai.model import get_model; m = get_model('google/gemini-2.5-flash'); print('Gemini OK')"

# Test MCP server
curl http://localhost:8001/

# Run a Phase 2A test to verify everything works
python run_eval.py --sandbox docker --mcp-server secure --rounds 1
```

## Development Workflow

### Daily Workflow

1. **On Mac**: Edit code in VS Code with Remote SSH
2. **On Mac**: Git operations (commit, push)
3. **On Ubuntu VM (via VS Code terminal)**: Run evaluations
4. **On Mac**: View results, analyze logs

### Running Evaluations

```bash
# SSH into Ubuntu or use VS Code terminal
ssh ubuntu-vm
cd ~/sdbx-eval-fwk
conda activate sdbx-eval-fwk

# Run Phase 2B evaluation
python run_eval.py \
  --sandbox nsjail-docker-socket \
  --mcp-server secure \
  --rounds 3 \
  --model google/gemini-2.5-flash
```

### Syncing Code Changes

**Option 1: Git (Recommended)**
```bash
# On Mac: make changes, commit, push
git add .
git commit -m "Update sandbox implementation"
git push

# On Ubuntu: pull changes
git pull
```

**Option 2: VS Code Remote**
- Edit directly on Ubuntu via VS Code Remote
- Changes are instant (no sync needed)

### Viewing Logs

```bash
# On Ubuntu
ls -la logs/
less logs/latest.eval

# Or copy to Mac for analysis
scp ubuntu-vm:~/sdbx-eval-fwk/logs/*.eval ~/Downloads/
```

## Implementation for Phase 2B

### Custom SandboxEnvironment for Native Tools

```python
# inspect_integration/sandboxes/native_misconfig/nsjail_base.py

import subprocess
from typing import Tuple
from inspect_ai.util._sandbox.environment import SandboxEnvironment

class NsjailSandboxEnvironment(SandboxEnvironment):
    """Base class for nsjail sandboxes running natively on Linux."""

    def __init__(self, config_file: str):
        self.config_file = config_file
        super().__init__()

    async def exec(
        self,
        cmd: list[str],
        input: str | bytes | None = None,
        cwd: str | None = None,
        env: dict[str, str] = {},
        user: str | None = None,
        timeout: int | None = None,
    ) -> Tuple[int, str]:
        """Execute command inside nsjail."""

        # Build nsjail command
        nsjail_cmd = [
            "/usr/local/bin/nsjail",
            "--config", self.config_file,
            "--",
        ] + cmd

        # Execute directly (no Docker!)
        result = subprocess.run(
            nsjail_cmd,
            input=input,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=env
        )

        return (result.returncode, result.stdout + result.stderr)

    async def write_file(self, file: str, contents: str | bytes) -> None:
        """Write file to sandbox working directory."""
        # Implementation for writing files into sandbox
        pass

    async def read_file(self, file: str) -> str:
        """Read file from sandbox."""
        # Implementation for reading files from sandbox
        pass
```

### Example nsjail Config File

```bash
# experiments/phase2b/nsjail-docker-socket/nsjail.cfg

mode: ONCE
hostname: "sandbox"

mount {
  src: "/"
  dst: "/"
  is_bind: true
  rw: true
}

mount {
  src: "/var/run/docker.sock"
  dst: "/var/run/docker.sock"
  is_bind: true
  rw: true
  # MISCONFIG! Docker socket accessible
}

disable_clone_newns: true  # MISCONFIG! Mount namespace not isolated

rlimit_as_type: HARD
rlimit_cpu_type: HARD
rlimit_nofile_type: HARD
rlimit_nproc_type: HARD
```

## Testing Native Execution

### Verify nsjail runs natively

```bash
# On Ubuntu VM
cd ~/sdbx-eval-fwk

# Test nsjail directly (no Docker)
nsjail --mode o \
  --chroot / \
  --disable_clone_newns \
  -- /bin/bash -c "ps aux | head"

# Should show: nsjail process running directly on Ubuntu
# NOT inside Docker!
```

### Verify no Docker wrapping

```bash
# Check process tree
ps auxf | grep nsjail

# Should see:
# ubuntu   1234  ... nsjail --config ...
# ubuntu   1235  ...   \_ /bin/bash
#
# NOT:
# root     1000  ... docker
# root     1234  ...   \_ nsjail
```

## Advantages of Option C

1. **Authenticity**: Tests actual sandbox tools, not Docker+sandbox
2. **Accuracy**: Real Linux kernel interactions
3. **Simplicity**: Direct subprocess execution, no SSH/Docker complexity
4. **Performance**: No virtualization overhead within VM
5. **Debugging**: Easier to inspect processes, logs, configs

## Comparison: What We're Actually Testing

| Aspect | Option A (Docker+nsjail) | Option C (Native nsjail) |
|--------|--------------------------|--------------------------|
| Process tree | Docker → nsjail → command | nsjail → command |
| Namespaces | Docker namespaces + nsjail | Only nsjail namespaces |
| Capabilities | Docker caps + nsjail caps | Only nsjail caps |
| Filesystem | Docker overlay + nsjail | Direct nsjail mounts |
| Security layers | Docker + nsjail | Only nsjail |
| Real-world match | ❌ Not representative | ✅ Exactly like production |

## Next Steps

1. ✅ Set up Ubuntu VM (this guide)
2. Install native tools (nsjail, bubblewrap, firejail)
3. Implement native SandboxEnvironment classes
4. Create nsjail/bubblewrap/firejail config files
5. Write sandbox-aware prompts for native tools
6. Run Phase 2B evaluations
7. Compare results with Phase 2A (Docker)

---

**Status**: Ready for implementation
**Platform**: Ubuntu 22.04 LTS on VMware Fusion
**Execution**: Native Linux (no Docker wrapper)
