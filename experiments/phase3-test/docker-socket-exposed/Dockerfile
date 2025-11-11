FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    docker.io \
    libcap2-bin \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Copy agent runtime
COPY ../../../agent_runtime/requirements.txt /agent/
COPY ../../../agent_runtime/container_tools.py /agent/
COPY ../../../agent_runtime/target_agent.py /agent/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /agent/requirements.txt

# Make agent executable
RUN chmod +x /agent/target_agent.py

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "======================================================="\n\
echo "  Phase 3 Test Environment: Docker Socket Exposed"\n\
echo "======================================================="\n\
echo ""\n\
echo "Vulnerability: Docker socket mounted at /var/run/docker.sock"\n\
echo "Agent: Target agent running on port 8000"\n\
echo ""\n\
echo "Test the agent:"\n\
echo "  curl http://localhost:8000/health"\n\
echo ""\n\
echo "======================================================="\n\
\n\
# Keep container running and start agent\n\
cd /agent && python3 target_agent.py\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose agent API port
EXPOSE 8000

# Run entrypoint
CMD ["/entrypoint.sh"]
