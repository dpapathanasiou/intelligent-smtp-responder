#!/bin/sh

# set_iptables.sh
# This script uses the 'iptables' command to redirect port 25 (conventional SMTP) traffic to port 8888 (where the smtp_server.py is running & listening)

# Make sure:
#  - smtp_server_port in config.py is also defined as 8888
#  - run this script as root/sudo
#  - it only needs to be called once!

# set the redirect: port 25 traffic to port 8888
iptables -t nat -A PREROUTING -p tcp --dport 25 -j REDIRECT --to-port 8888

# confirm the redirect is there
iptables -t nat -L

# no need to restart networking,
# but create an /etc/iptables.up.rules file
# to make the redirect take effect on reboot.

# For more details read:
# http://articles.slicehost.com/2011/2/21/introducing-iptables-part-3
# or
# https://wiki.debian.org/iptables

# if you ever need to remove the redirect,
# run the unset_iptables.sh script in this
# folder, and update or remove /etc/iptables.up.rules
# as necessary

