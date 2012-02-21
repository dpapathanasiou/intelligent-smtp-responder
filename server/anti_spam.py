#!/usr/bin/python

"""

Functions to prevent spam by ignoring ip and subject combinations which occur too frequently, and are likely to be from spammers or bots, etc.
Based on concept described by Paul Tyma: http://mailinator.blogspot.com/2007/01/architecture-of-mailinator.html

"""

import time

ip_hash      = {} # k=ip address,   v=(tuple: timestamp (universal) when key was added, frequency)
subject_hash = {} # k=subject line, v=(tuple: timestamp (universal) when key was added, frequency)

aging_hash_interval    = 120.0 # 2 minutes
ip_hash_threshold      = 20    # number of occurences within aging_hash_interval which are tolerated for the ip_hash
subject_hash_threshold = 120   # number of occurences within aging_hash_interval which are tolerated for the subject hash
                               # (this is higher than the ip_hash_threshold since the same subject may be part of a longer conversation thread)

def dump_hash (aging_hash):
    """For debugging: print the contents of the aging hash"""

    for k, v in aging_hash.items():
        print "%s\t%s" % (k, v)

def purge_expired (aging_hash, interval=aging_hash_interval):
    """Remove everything in the given hash if it has exceeded the given time interval"""

    expired = []
    for k, v in aging_hash.items():
        set_time = v[0]
        if (time.time() - set_time) > aging_hash_interval:
            expired.append(k)
    for ex_k in expired:
        del aging_hash[ex_k]

def update_aging_hash (aging_hash, k, increment=1):
    """Add key k to the aging hash if not already present"""

    if not aging_hash.has_key(k):
        aging_hash[k] = (time.time(), increment)
    else:
        current_val = aging_hash[k]
        aging_hash[k] = (current_val[0], increment + current_val[1])
    return aging_hash[k]

def valid_key (k, aging_hash, frequency_threshold):
    """Determine whether or not this key k is valid, based on number of appearances versus the specified threshold"""

    purge_expired(aging_hash)
    current_val = update_aging_hash(aging_hash, k)
    return current_val[1] <= frequency_threshold


# public methods

def valid_ip_address (ip_address):
    """Determine if this ip is valid, based on the number of occurences within the aging time interval"""
    return valid_key(ip_address, ip_hash, ip_hash_threshold)

def valid_subject (subject):
    """Determine if this ip and subject combination is valid, based on the number of occurences within the aging time interval"""
    return valid_key(subject, subject_hash, subject_hash_threshold)

def block_ip_address (ip_address):
    """Block this ip address by adding it to the ip_hash with a large occurence count"""
    update_aging_hash(ip_hash, ip_address, ip_hash_threshold)

def block_subject (subject):
    """Block this subject by adding it to the subject_hash with a large occurence count"""
    update_aging_hash(subject_hash, subject, subject_hash_threshold)
