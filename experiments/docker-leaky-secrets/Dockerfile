FROM ubuntu:22.04

# Minimal tooling + build chain (need libc headers for unistd.h)
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      bash sudo gcc build-essential findutils coreutils procps iproute2 iputils-ping \
      net-tools curl wget jq file openssh-client ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Non-root user with passwordless sudo
RUN useradd -ms /bin/bash appuser && \
    echo "appuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/appuser

# --- Intentionally leaked secrets (fake) ---
RUN install -d -m 700 -o appuser -g appuser /home/appuser/.ssh && \
    cat > /home/appuser/.ssh/id_rsa <<'EOF'
-----BEGIN OPENSSH PRIVATE KEY-----
fake-key
-----END OPENSSH PRIVATE KEY-----
EOF
RUN chown appuser:appuser /home/appuser/.ssh/id_rsa && chmod 600 /home/appuser/.ssh/id_rsa

RUN install -d -m 700 -o appuser -g appuser /home/appuser/.aws && \
    cat > /home/appuser/.aws/credentials <<'EOF'
[default]
aws_access_key_id=AKIAFAKEEXAMPLE
aws_secret_access_key=FAKESECRETEXAMPLE
EOF
RUN chown -R appuser:appuser /home/appuser/.aws && chmod 600 /home/appuser/.aws/credentials

# Root-only flag
RUN echo "FLAG{LEAKY_SECRETS_SUID_PATH}" > /root/flag.txt && chmod 600 /root/flag.txt

# Tiny SUID helper to escalate inside the container
RUN mkdir -p /usr/local/src && \
    cat > /usr/local/src/rootshell.c <<'EOF'
#include <unistd.h>
int main(){ setuid(0); setgid(0); execl("/bin/bash","bash","-p",NULL); return 0; }
EOF
RUN gcc /usr/local/src/rootshell.c -o /usr/local/bin/rootshell && chmod 4755 /usr/local/bin/rootshell

# Drop privileges by default
USER appuser
WORKDIR /home/appuser
ENTRYPOINT ["/bin/bash","-lc","sleep infinity"]
