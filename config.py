
domain_logo = "example.org" # this is just for illustration; use your own domain here
server_auto_email = "noreply@example.org"

# override these settings with local_config.py as needed
smtp_server_domain = "example.org"  # use this when running on your server (and replace this definition with your own domain)
smtp_server_port   = 8888 # port for the custom SMTP server (iptables will redirect port 25 here: see set_iptables.sh)
smtp_server_debug  = False # if True, this logs all the incoming client activity and writes it to stdout
send_outgoing_eml  = True  # if False, emailer.send() merely prints the message to stdout instead of sending it

# define the list of email addresses @smtp_server_domain which get sent to the pass_through_target address as-is with no auto-reply

pass_through_mailboxes = [ 'admin', 'administrator', 'hostmaster', 'root', 'webmaster', 'postmaster', ]
pass_through_target = 'support@example.com' # ideally, use an email address on a different server and domain than the one running this code

# 3rd party API keys 

forecast_io_key = '[for weather results (use the real API key here or in local_config.py)]'

# define the dict of email addresses @smtp_server_domain which invoke a specific function

action_mailboxes = {

    # k = email inbox : v = module.threaded class to run (modules must be defined in agents)

    'current-time' : 'time_response_example.reply_time',
    'nyc-weather'  : 'weather_response_example.reply_nyc_weather',
    'weather'      : 'weather_response_example.reply_weather',
}

default_mailbox = None # if defined, as a string in the form module.class, it will be invoked as the default responder (must be defined in agents)

# override any of the above settings for the local environment
# e.g., change smtp_server_domain to 'localhost' for testing, etc.
# the local_config.py file is not checked into source control

try:
    from local_config import *
except ImportError:
    pass
