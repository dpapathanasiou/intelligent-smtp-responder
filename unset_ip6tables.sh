#!/bin/sh

# unset_ip6tables.sh
# This script uses the 'ip6tables' command to remove the IPv6 port redirect established by set_ip6tables.sh
# Just like set_ip6tables.sh, you need to run this script as root/sudo

# Remove the redirect established by set_ip6tables.sh
ip6tables -t mangle -F

# confirm the redirect is gone
ip6tables -t mangle -L

# remove the /etc/ip6tables.up.rules and /etc/network/if-pre-up.d/iptables files

