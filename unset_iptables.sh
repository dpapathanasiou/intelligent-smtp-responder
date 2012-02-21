#!/bin/sh

# unset_iptables.sh
# This script uses the 'iptables' command to remove the port 25 to port 8888 redirect established by set_iptables.sh
# Just like set_iptables.sh, you need to run this script as root/sudo

# Remove the redirect established by set_iptables.sh
iptables -t nat -F

# confirm the redirect is gone
iptables -t nat -L

# restart networking to make the change take effect
# (this command is for debian/ubuntu - check your distro for the specific command)
/etc/init.d/networking stop; /etc/init.d/networking start

