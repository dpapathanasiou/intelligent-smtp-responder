#!/bin/sh

# set_ip6tables.sh
# This script uses the 'ip6tables' command to redirect IPv6 
# smtp port traffic to port 8888 (where the smtp_server.py is running & listening)

# Make sure:
#  - smtp_server_port in config.py is also defined as 8888
#  - run this script as root/sudo
#  - it only needs to be called once!

# set the redirect: smtp port traffic to port 8888
ip6tables -A PREROUTING -t mangle -p tcp --dport 25 -j TPROXY --on-port 8888

# confirm the redirect is there
ip6tables -t mangle -L

# no need to restart networking 
# but create an /etc/ip6tables.up.rules file
# and make it active on reboot, using ip6tables-save/-restore

