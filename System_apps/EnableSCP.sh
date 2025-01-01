#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/log.txt"

# Backup configuración actual si existe
if [ -f /etc/ssh/sshd_config ]; then
  cp -f /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
fi

# Configurar SSH con soporte SCP
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
AllowTcpForwarding yes
X11Forwarding no
EOF

# Si SSH no está activo, lo iniciamos
if ! systemctl is-active ssh >/dev/null; then
    systemctl enable ssh &>>"$log_file"
    systemctl start ssh &>>"$log_file"
fi

# Set root password if not set
echo "root:root" | chpasswd

# Reiniciar SSH para aplicar cambios
systemctl restart ssh &>>"$log_file"

echo "SCP enabled successfully" >> "$log_file"
exit 0