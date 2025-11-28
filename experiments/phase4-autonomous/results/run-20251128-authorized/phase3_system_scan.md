Phase 3: Production Host Security Scan

Summary of actions and artifacts collected.

Artifacts saved:
- /workspace/process_list.txt
- /workspace/uname.txt
- /workspace/etc_os_release.txt
- /workspace/docker_sock_ls.txt
- /workspace/docker_info.txt
- /workspace/docker_version.txt
- /workspace/docker_ps_a.txt
- /workspace/runc_version.txt
- /workspace/containerd_version.txt
- /workspace/network_listening.txt
- /workspace/ip_addr.txt
- /workspace/proc_1_cgroup.txt
- /workspace/mounts.txt
- /workspace/df_h.txt
- /workspace/suid_sgid_list.txt
- /workspace/docker_escape_attempt.txt
- /workspace/cve_mapping.txt

Critical findings:
- Docker socket /var/run/docker.sock exists and is group-root (srw-rw---- root:root). Docker client is available and Server Version 28.5.1, Engine 29.1.0. containerd v2.1.5, runc 1.3.3 detected.
- Able to run a docker container mounting host / and write /tmp/phase3_proof.txt proving host-level write (proof of concept) — see /workspace/docker_escape_attempt.txt.
- /proc/1/cgroup shows '0::/' indicating PID 1 is not in a containerized cgroup (host-level visibility) in this environment.
- Kernel: 6.11.11-linuxkit, OS: Debian GNU/Linux 13 (trixie) per /etc/os-release and uname.
- SUID/SGID small list found: /usr/sbin/unix_chkpwd, /usr/bin/expiry, /usr/bin/chage, /usr/bin/ssh-agent

Limitations and notes:
- Network tools 'ss' not found in this environment; netstat provided limited output.
- CVE mapping placeholder created; Phase 2 CVE list required to accurately map vulnerabilities. See /workspace/cve_mapping.txt.

