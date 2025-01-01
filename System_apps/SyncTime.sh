#!/bin/bash

appdir=$(dirname -- "$0")
log_file="${appdir}/log.txt"

# Instalar dependencias necesarias
echo "Installing required packages..." >> "$log_file"
apt-get update -y &>> "$log_file"
apt-get install -y ntpdate curl tzdata &>> "$log_file"

# Establecer zona horaria por defecto a Asia/Shanghai si no se puede detectar
DEFAULT_TIMEZONE="America/Chicago"

# Intentar obtener la zona horaria
if command -v curl &> /dev/null; then
    timezone=$(curl -s http://ip-api.com/line?fields=timezone)
else
    timezone=$DEFAULT_TIMEZONE
fi

if [ -z "$timezone" ]; then
    timezone=$DEFAULT_TIMEZONE
fi

# Establecer la zona horaria
echo "Setting timezone to $timezone" >> "$log_file"
timedatectl set-timezone "$timezone" &>> "$log_file"

# Sincronizar la hora con servidores NTP de China
echo "Synchronizing time..." >> "$log_file"
ntpdate -u ntp.aliyun.com &>> "$log_file" || \
ntpdate -u ntp1.aliyun.com &>> "$log_file" || \
ntpdate -u ntp2.aliyun.com &>> "$log_file" || \
ntpdate -u ntp.ntsc.ac.cn &>> "$log_file"

# Actualizar el reloj del hardware
hwclock --systohc

echo "Time synchronized successfully" >> "$log_file"
exit 0