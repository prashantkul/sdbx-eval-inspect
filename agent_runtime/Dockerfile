FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libcap2-bin \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /agent

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY container_tools.py .
COPY target_agent.py .

# Make agent executable
RUN chmod +x target_agent.py

# Default command - keep container running for LangGraph invocation
CMD ["tail", "-f", "/dev/null"]
