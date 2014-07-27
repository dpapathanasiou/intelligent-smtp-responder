#!/usr/bin/python

"""

The custom smtp server: respond to all incoming email based on its inbox address

"""

import re
import time
import socket, SocketServer
from statemachine import StateMachine
from anti_spam import valid_ip_address, valid_subject, block_ip_address

from config import domain_logo, smtp_server_domain, smtp_server_port, smtp_server_debug
from utils.email_utils import valid_email_address, get_email_address, domain_recipients_valid, get_base_subject
from smtp_processor import process_email

cr_lf = "\r\n"
bad_request = '550 No such user'
idle_threshold = 600.0 # client must complete the interaction within 10 min or be cut-off

recipient_domain = domain_logo.lower() # used to check rcpt to values by domain

def printException (ex_args):
    data = {}
    try:
        if isinstance(ex_args, tuple):
            data[ex_args[0]] = ex_args[1]
        else:
            data['state'] = ex_args[0]['state']
            if ex_args[0]['data']:
                for k,v in ex_args[0]['data'].items():
                    if k in ['ip', 'start', 'sender', 'recipients', 'subject']:
                        data[k] = v
    except IndexError as i:
        pass
    except KeyError as k:
        pass
    print 'Exception:', time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), data

def with_stream (fn, *args):
    """A higher-order function to attempt stream functions, trapping any socket errors which may occur"""
    try:
        return fn(*args)
    except socket.error, e:
        if isinstance(e.args, tuple):
            printException (e.args)
        else:
            printException ({"Socket error":e})

def with_stream_write (st, s):
    """Write the given string (s) to the stream (st)"""
    with_stream(lambda: st.wfile.write(s))

def with_stream_read (st):
    """Read a line from the given stream (st)"""
    data = with_stream(lambda: st.rfile.readline())
    if data is None:
        return '' # always return a string, even if there was a socket error
    else:
        return data

def client_is_idle (start_time, threshold=idle_threshold):
    """Has this client taken longer than allowed by idle_threshold?"""
    return (time.time() - start_time) > threshold

def as_timed_client (cargo, fn):
    """Enforce the idle_threshold condition here:
    stop the client with a bad request reply and close the connection if idle_threshold has been exceeded;
    else proceed with the given function"""
    if client_is_idle(cargo[1]['start']):
        with_stream_write (cargo[0], bad_request+cr_lf)
        return ('done', cargo)
    else:
        return fn()

def greeting (cargo):
    stream = cargo[0]
    ip = stream.client_address[0]
    if not valid_ip_address(ip):
        with_stream_write (stream, bad_request+cr_lf)
        return ('done', cargo)
    else:
        with_stream_write (stream, '220 '+domain_logo+' SMTP'+cr_lf)
        email_data = cargo[1]
        email_data['ip'] = ip
        email_data['start'] = time.time()
        return ('helo', (stream, email_data))

helo_pattern = re.compile('^HELO', re.IGNORECASE)
ehlo_pattern = re.compile('^EHLO', re.IGNORECASE)

def helo (cargo):
    def _helo ():
        stream = cargo[0]
        client_msg = with_stream_read (stream)

        if smtp_server_debug:
            print 'Debug:', cargo[1]['ip'], time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), client_msg.rstrip('\r\n')

        if helo_pattern.search(client_msg) or ehlo_pattern.search(client_msg):
            with_stream_write (stream, '250 Hello'+cr_lf)
            return ('mail', cargo)
        else:
            with_stream_write (stream, bad_request+cr_lf)
            return ('done', cargo)
    return as_timed_client(cargo, _helo)

mail_pattern = re.compile('^MAIL', re.IGNORECASE)

def mail (cargo):
    def _mail ():
        stream = cargo[0]
        client_msg = with_stream_read (stream)

        if smtp_server_debug:
            print 'Debug:', cargo[1]['ip'], time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), client_msg.rstrip('\r\n')

        if mail_pattern.search(client_msg):
            sender = get_email_address(client_msg)
            if sender is None or not valid_email_address(sender):
                with_stream_write (stream, bad_request+cr_lf)
                return ('done', cargo)
            else:
                with_stream_write (stream, '250 Ok'+cr_lf)
                email_data = cargo[1]
                email_data['sender'] = sender
                return ('rcpt', (stream, email_data))
        else:
            with_stream_write (stream, bad_request+cr_lf)
            return ('done', cargo)
    return as_timed_client(cargo, _mail)

rcpt_pattern = re.compile('^RCPT', re.IGNORECASE)
data_pattern = re.compile('^DATA', re.IGNORECASE)

def rcpt (cargo):
    stream = cargo[0]
    email_data = cargo[1]

    recipients = []
    client_error = False

    while 1:
        client_msg = with_stream_read (stream)

        if smtp_server_debug:
            print 'Debug:', cargo[1]['ip'], time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), client_msg.rstrip('\r\n')

        if client_is_idle(email_data['start']):
            client_error = True
            break
        elif rcpt_pattern.search(client_msg):
            recipient = get_email_address(client_msg)
            if recipient is None or not valid_email_address(recipient):
                client_error = True
                break
            else:
                if recipient not in recipients:
                    recipients.append(recipient)
                with_stream_write (stream, '250 Ok'+cr_lf)
        elif data_pattern.search(client_msg):
            break
        else:
            client_error = True
            break

    # get the list of email addresses specified in the 'RCPT TO:' portion of the message
    server_recipients = filter(lambda x: x.split('@')[1].lower() == recipient_domain, recipients)
    # find the inbox @smtp_server_domain which is valid (i.e., we have an action function or pass-through specified)
    inbox = domain_recipients_valid(map(lambda x: x.split('@')[0].lower(), server_recipients))
    if inbox is None:
        block_ip_address(email_data['ip'])
        client_error = True

    if client_error or len(server_recipients) == 0:
        # this email was not sent to an inbox that we can respond to
        # so stop the client with a bad request reply and close the connection 
        with_stream_write (stream, bad_request+cr_lf)
        return ('done', cargo)
    else:
        email_data['inbox'] = inbox
        email_data['recipients'] = recipients
        return ('data', (stream, email_data))

end_pattern = re.compile('^.$')
subject_pattern = re.compile('^Subject: ', re.IGNORECASE)

def data (cargo):
    stream = cargo[0]
    email_data = cargo[1]

    with_stream_write (stream, '354 End data with \\r\\n.\\r\\n'+cr_lf)

    contents = []
    client_error = False
    subject = None

    while 1:
        client_msg = with_stream_read (stream)
        if client_is_idle(email_data['start']):
            client_error = True
            break
        elif end_pattern.search(client_msg.rstrip()):
            break
        else:
            contents.append(client_msg)
            if subject is None:
                if subject_pattern.search(client_msg):
                    try:
                        subject = filter(lambda x: x!='', re.split(subject_pattern, client_msg))[0].lstrip()
                        email_data['subject'] = get_base_subject(subject)
                        if not valid_subject(subject):
                            client_error = True
                            break
                    except IndexError:
                        pass

    if client_error or len(contents) == 0:
        with_stream_write (stream, bad_request+cr_lf)
        return ('done', cargo)
    else:
        with_stream_write (stream, '250 Ok: queued'+cr_lf)
        email_data['contents'] = ''.join(contents)
        return ('process', (stream, email_data))

def process (cargo):
    # if the state machine has gotten this far, the email is valid, so pass it to the processor
    process_email(cargo[1]) 
    return ('done', cargo)


class SMTPRequestHandler (SocketServer.StreamRequestHandler):
    def handle (self):
        m = StateMachine()
        try:
            m.add_state('greeting', greeting)
            m.add_state('helo', helo)
            m.add_state('mail', mail)
            m.add_state('rcpt', rcpt)
            m.add_state('data', data)
            m.add_state('process', process)
            m.add_state('done', None, end_state=1)
            m.set_start('greeting')

            m.run((self, {}))

        # in the event of an exception, capture the current
        # state and cargo dict and use the information
        # as part of the message sent to stdout
        except Exception as e:
            exception_data = {'state':m.current_state}
            if m.current_cargo:
                exception_data['data'] = m.current_cargo[1]
            e.args = (exception_data,)
            raise
        
def start():
    try:
        tcpserver = SocketServer.ThreadingTCPServer((smtp_server_domain, smtp_server_port), SMTPRequestHandler)
        tcpserver.socket.settimeout(idle_threshold)
        tcpserver.serve_forever()
    except Exception as e:
        printException (e.args)

if __name__ == '__main__':
    start()
