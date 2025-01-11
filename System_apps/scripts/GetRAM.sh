#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/../log.txt"

# Get total RAM in MB
total=$(free -m | awk '/^Mem:/{print $2}')

# Get used RAM in MB
used=$(free -m | awk '/^Mem:/{print $3}')

# Get available RAM in MB
available=$(free -m | awk '/^Mem:/{print $7}')

# Calculate usage percentage
usage_percent=$(awk "BEGIN {printf \"%.1f\", ($used/$total)*100}")

echo "{\"total\": $total, \"used\": $used, \"available\": $available, \"usage_percent\": $usage_percent}" > "$log_file"
exit 0