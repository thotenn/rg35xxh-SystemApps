#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/log.txt"

echo "Installing required packages..."
apt-get update -y &>> "$log_file"
apt-get install -y ntpdate curl tzdata

DEFAULT_TIMEZONE="America/Chicago"

if command -v curl &> /dev/null; then
    timezone=$(curl -s http://ip-api.com/line?fields=timezone)
else
    timezone=$DEFAULT_TIMEZONE
fi

if [ -z "$timezone" ]; then
    timezone=$DEFAULT_TIMEZONE
fi

echo "Setting timezone to $timezone"
timedatectl set-timezone "$timezone"

echo "Synchronizing time..."
ntpdate -u ntp.aliyun.com || \
ntpdate -u ntp1.aliyun.com || \
ntpdate -u ntp2.aliyun.com || \
ntpdate -u ntp.ntsc.ac.cn

hwclock --systohc

echo "Time synchronized successfully" >> "$log_file"
exit 0