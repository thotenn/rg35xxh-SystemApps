#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/../logs/ssh-manager.log"

# Restore original config if exists
if [ -f "/etc/ssh/sshd_config.backup" ]; then
  mv -f /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
fi

# Disable and stop SSH
systemctl disable ssh &>>"$log_file"
systemctl stop ssh &>>"$log_file"

echo "SSH disabled successfully" >> "$log_file"
exit 0