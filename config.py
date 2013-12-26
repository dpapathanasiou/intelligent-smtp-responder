
domain_logo = "example.org" # this is just for illustration; use your own domain here
server_auto_email = "noreply@example.org"

# override these settings with local_config.py as needed
smtp_server_domain = "example.org"  # use this when running on your server (and replace this definition with your own domain)
smtp_server_port   = 8888 # port for the custom SMTP server (iptables will redirect port 25 here: see set_iptables.sh)
smtp_server_debug  = False # if True, this logs all the incoming client activity and writes it to stdout


# define the list of email addresses @smtp_server_domain which get sent to the pass_through_target address as-is with no auto-reply

pass_through_mailboxes = [ 'admin', 'administrator', 'hostmaster', 'root', 'webmaster', 'postmaster', ]
pass_through_target = 'support@example.com' # ideally, use an email address on a different server and domain than the one running this code


# define the dict of email addresses @smtp_server_domain which invoke a specific function

action_mailboxes = {

    # k = email inbox : v = threaded class to run (must be defined in agents/responders.py)

    'current-time' : 'reply_time',
    'nyc-weather'  : 'reply_nyc_weather',
}


# override any of the above settings for the local environment
# e.g., change smtp_server_domain to 'localhost' for testing, etc.
# the local_config.py file is not checked into source control

try:
    from local_config import *
except ImportError:
    pass
