#!/bin/sh

# unset_iptables.sh
# This script uses the 'iptables' command to remove the port 25 to port 8888 redirect established by set_iptables.sh
# Just like set_iptables.sh, you need to run this script as root/sudo

# Remove the redirect established by set_iptables.sh
iptables -t nat -F

# confirm the redirect is gone
iptables -t nat -L

# If you had created or edited an /etc/iptables.up.rules file
# to make the redirect take effect on reboot, you should remove
# or edit it accordingly.

# For more details read:
# http://articles.slicehost.com/2011/2/21/introducing-iptables-part-3
# or
# https://wiki.debian.org/iptables
