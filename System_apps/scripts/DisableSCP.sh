#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/../log.txt"

# Configurar SSH sin soporte SCP
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
AllowTcpForwarding no
X11Forwarding no
EOF

# Reiniciar SSH para aplicar cambios
systemctl restart ssh &>>"$log_file"

echo "SCP disabled successfully" >> "$log_file"
exit 0