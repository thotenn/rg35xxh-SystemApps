#!/bin/bash

. /mnt/mod/ctrl/configs/functions &>/dev/null 2>&1
progdir=$(cd $(dirname "$0"); pwd)

program="python3 ${progdir}/System_apps/main.py"
log_file="${progdir}/System_apps/log.txt"

$program > "$log_file" 2>&1