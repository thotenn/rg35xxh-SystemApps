#!/bin/bash

# Sync filesystem to ensure data is written to disk
sync

# Clear page cache, dentries and inodes
echo 3 > /proc/sys/vm/drop_caches

# Optional: Clear swap if present
swapoff -a 2>/dev/null
swapon -a 2>/dev/null