intelligent-smtp-responder
==========================

This is an intelligent email-based agent server, written in Python,
using state machine logic to handle the SMTP protocol.

The server works by responding to email sent to designated inboxes with
canned, dynamic, or custom replies.

Among the included examples, email sent to <tt>nyc-weather@</tt> will be
automatically replied with the current forecast for NYC, using data from
the National Weather Service website.

The basic examples do not take account the sender, subject, or email
message text, but the server can be extended with natural language
processing and other AI techniques to provide more customized
auto-replies.

This code is loosely based on [Paul Tyma's](http://paultyma.blogspot.com/) [Mailinator]
(http://mailinator.com/) in that it does not support the full range
of SMTP commands, and instead uses ip traps and timeouts to foil
spammers and other scripts or bots, continuing [the work described here]( http://denis.papathanasiou.org/2011/11/11/re-creating-mailinator-in-python/).

It also forms the basis for the server used by the [TeamWork.io]
(http://teamwork.io/) web service.

Installation
------------

Clone this repo, and make sure you have [pycurl](http://pycurl.sourceforge.net/) and [lxml](http://lxml.de/) installed (using [pip](http://www.pip-installer.org/en/latest/) is recommended):

```
git clone https://github.com/dpapathanasiou/intelligent-smtp-responder.git
sudo pip install pycurl
sudo pip install lxml
```

Optionally install [libmagic](http://sourceforge.net/projects/libmagic/) for python since it is helpful for identifying mime types found in email messages (though this code will run without it):

```
sudo apt-get install python-magic
```

<i>Important:</i> there is a suble but important difference between [the package available via pip](http://pypi.python.org/pypi/python-magic/) versus [what apt installs](http://packages.ubuntu.com/search?keywords=python-magic). The code in [emailer.py](utils/emailer.py) depends on the latter.

Getting Started
---------------

 <i>Note that this server listens to incoming requests, but it does NOT
 provide a way to send outbound emails, so make sure you have a outgoing
 mail server such as [Postfix](http://www.postfix.org/) installed and running.</i>

 1. Edit the [config.py](config.py) file in this folder and redefine these variables with your server's domain instead of <tt>example.org</tt>:
```
domain_logo         = "example.org"
server_auto_email   = "noreply@example.org"
smtp_server_domain  = "example.org"
pass_through_target = "support@example.com"
```
 Ideally, the <tt>pass_through_target</tt> email address resides on a different server than the one running this code.

 2. Edit the <tt>action_mailboxes</tt> dict in the [config.py](config.py) file.

 Each key is the name of the inbox you want the server to auto-respond to, and the
 value is the name of the function which carries out the request. 

 Each function needs to be implemented in the [responders.py](agents/responders.py) file. See the notes in that file for the functional prototype requirements, and also look at the [examples](agents/responders.py#L72) provided.

 3. (optional) Edit the <tt>pass_through_mailboxes</tt> list in the [config.py](config.py) file. 

 These are the inboxes which the server ignores, and just passes through to the email address defined by the <tt>pass_through_target</tt> variable.

 4. (optional) For logging, set the <tt>smtp_server_debug variable</tt> to <tt>True</tt>

 This will record the ip address, timestamp, and all commands up to
 DATA sent to the server by each client.

 5. Run the [set_iptables.sh](set_iptables.sh) script as root or sudo: 
```
sh ./set_iptables.sh
```

 The default port for redirecting incoming traffic is 8888, but you can change that as necessary.
 
 If you're not using debian/ubuntu you'll need to edit the line for restarting your machine's networking service accordingly.

 You can always undo the iptables setting by running the <tt>unset_iptables.sh</tt> script as root/sudo.

 6. Edit the [run_smtps.sh](run_smtps.sh) file.

 By default, the server runs as user <tt>daemon</tt>, but if your auto-responder agents need access to different resources/user groups, just change the user defined at the end of this line:
```sh
su -c "export PYTHONPATH=$PYTHONPATH:$smtps:$smtps/server:$smtps/utils:$smtps/agents; python -c 'import smtp_server; smtp_server.start()' > /tmp/smtp_server_$logfile.log 2>&1" daemon
```

 The script is designed to restart in case of an error, and if you'd like to get the log by email when that happens, change the target email address in this line:
```sh
mail -s "SMTP server error!" support@example.org < /tmp/smtp_server_$logfile.log
```

 Note that logfiles do not over-write each other, so you can remove that line altogether, if you'd rather not get the alert.

 7. Start the server as root/sudo: 
```sh
sh ./run_smtps.sh
```

 If you'll be running it long-term, it's best to kick this off inside a [screen session](http://www.tldp.org/LDP/GNU-Linux-Tools-Summary/html/virtual-terminals.html), from which you can detach.

Acknowledgements
----------------

* [Paul Tyma](http://paultyma.blogspot.com/) for his description of how [Mailinator](http://mailinator.com/) works
* [Ian Lewis](https://github.com/IanLewis) for the [email parsing logic](http://www.ianlewis.org/en/parsing-email-attachments-python) in the [email_parser.py](server/email_parser.py) file
