#!/bin/bash

# Log file setup
log_file="cleanup.log"

# Clean package cache
apt-get clean >> "$log_file" 2>&1

# Remove unused packages and dependencies
apt-get autoremove -y >> "$log_file" 2>&1

# Remove old config files
apt-get purge -y $(dpkg -l | awk '/^rc/ {print $2}') >> "$log_file" 2>&1

# Clean up any remaining dependencies
apt-get autoclean >> "$log_file" 2>&1