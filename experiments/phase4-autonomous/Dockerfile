FROM python:3.11-slim

# Build argument for sandbox type
ARG SANDBOX_TYPE=medium

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    procps \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI for medium difficulty (socket will be mounted)
RUN if [ "$SANDBOX_TYPE" = "medium" ]; then \
        curl -fsSL https://get.docker.com -o get-docker.sh && \
        sh get-docker.sh && \
        rm get-docker.sh; \
    fi

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Copy requirements and install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY task_definitions.py /app/task_definitions.py
COPY custom_tools.py /app/custom_tools.py
COPY autonomous_agent.py /app/autonomous_agent.py
COPY behavior_classifier.py /app/behavior_classifier.py

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Create non-root user for hard mode
RUN if [ "$SANDBOX_TYPE" = "hard" ]; then \
        useradd -m -s /bin/bash agent && \
        chown -R agent:agent /workspace; \
    fi

# Set working directory
WORKDIR /app

# Default command (will be overridden by orchestrator)
CMD ["python", "-u", "autonomous_agent.py"]
