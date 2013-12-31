#!/usr/bin/python

"""

Functions for sending emails with attachments

Based on this snippet: http://snippets.dzone.com/posts/show/757 and updated to handle both binary and non-binary attachments according to their MIME types, as described here: http://denis.papathanasiou.org/?p=392

"""

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email.Header import Header
from email import Encoders
import os

import sys
from config import server_auto_email, send_outgoing_eml

def to_unicode (s):
    """Convert the given byte string to unicode, using the standard encoding,
    unless it's already encoded that way"""
    if s:
        if isinstance(s, unicode):
            return s
        else:
            return unicode(s, 'utf-8')

def to_bytestring (s):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode('utf-8')

MIME_MAGIC = None
try:
    import magic
    MIME_MAGIC = magic.open(magic.MAGIC_MIME)
    MIME_MAGIC.load()
except ImportError:
    pass

def get_file_mimetype (filename):
    """Return the mimetype string for this file"""
    result = None
    if MIME_MAGIC:
        try:
            result = MIME_MAGIC.file(filename)
        except IOError:
            pass
    return result


mail_server = 'localhost'


def send(subject, text, recipient_list=[], html=None, files=[], sender=None, replyto=None):
    """Send a message to the given recipient list, with the optionally attached files"""

    if not sender:
        sender = server_auto_email

    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(map(lambda x: x.encode('ascii'), recipient_list)) # make sure email addresses do not contain non-ASCII characters
    if replyto:
        msg['Reply-To'] = replyto.encode('ascii') # make sure email addresses do not contain non-ASCII characters
    msg['Date'] = formatdate(localtime=True)

    # always pass Unicode strings to Header, otherwise it will use RFC 2047 encoding even on plain ASCII strings
    msg['Subject'] = Header(to_unicode(subject), 'iso-8859-1') 

    # always use Unicode for the body text, both plain and html content types
    msg.attach(MIMEText(to_bytestring(text), 'plain', 'utf-8'))
    if html:
        msg.attach(MIMEText(to_bytestring(html), 'html', 'utf-8'))

    for file in files:
        file_read_flags = "rb"
        mimestring = get_file_mimetype(file)
        if not mimestring:
            part = MIMEBase('application', "octet-stream")
        else:
            if mimestring.startswith('text'):
                file_read_flags = "r"
            mimestring_parts = mimestring.split('/')
            if len(mimestring_parts) == 2:
                part = MIMEBase(mimestring_parts[0], mimestring_parts[1])
            else:
                part = MIMEBase(mimestring)
        part.set_payload( open(file, file_read_flags).read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                       % os.path.basename(file))
        msg.attach(part)

    if not send_outgoing_eml:
        # write the message to stdout
        # instead of actually sending it
        print 'From:', sender, '\nTo:', ', '.join(recipient_list), '\n', msg.as_string()
    else:
        # go ahead and send it
        smtp = smtplib.SMTP(mail_server)
        smtp.sendmail(sender, recipient_list, msg.as_string() )
        smtp.close()


if __name__ == "__main__":
    # a simple command-line interface to send one email at a time
    if len(sys.argv) < 4:
        print "\n\nUsage:\n\nemailer [recipient email address] [subject] [message] [(optional) /path/to/file to attach]"
    else:
        files = []
        if len(sys.argv) == 5:
            files = [sys.argv[4]]
        send(sys.argv[2], sys.argv[3], recipient_list=[sys.argv[1]], files=files)
