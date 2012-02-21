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

# restart networking to make the change take effect
# (this command is for debian/ubuntu - check your distro for the specific command)
/etc/init.d/networking stop; /etc/init.d/networking start

# if you ever need to remove the redirect, type this as root/sudo and restart networking:
#iptables -t nat -F
