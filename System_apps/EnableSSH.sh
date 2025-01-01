#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/ssh-manager.log"

# Install OpenSSH server if it doesn't exist
if ! systemctl list-units --full --all | grep -Fqi "ssh.service"; then
  echo 'Installing OpenSSH server...' >> "$log_file"
  echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections
  DEBIAN_FRONTEND="noninteractive" apt-get update -y --fix-missing \
    &>>"$log_file"
  DEBIAN_FRONTEND="noninteractive" apt-get install -y openssh-server \
    &>>"$log_file"
fi

# Backup and configure sshd
if [ -f /etc/ssh/sshd_config ]; then
  cp -f /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
fi

# Create minimal SSH config for SSH access
cat > /etc/ssh/sshd_config << EOF
Port 22
PermitRootLogin yes
StrictModes no
PasswordAuthentication yes
ChallengeResponseAuthentication no
UsePAM yes
PrintMotd no
UseDNS no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server
EOF

# Enable and start SSH
systemctl enable ssh &>>"$log_file"
systemctl start ssh &>>"$log_file"

# Set root password if not set
echo "root:root" | chpasswd

# Restart SSH to apply changes
systemctl restart ssh &>>"$log_file"

echo "SSH enabled successfully" >> "$log_file"
exit 0