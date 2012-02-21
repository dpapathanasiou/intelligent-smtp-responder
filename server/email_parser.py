#!/usr/bin/python

"""

Functions to parse email messages sent through the DATA portion of the server.
Based on: http://www.ianlewis.org/en/parsing-email-attachments-python

"""

from email.Header import decode_header
from email.Parser import Parser as EmailParser
from cStringIO import StringIO

unicode_encoding = 'utf8'
header_parts = ['From', 'To', 'Subject', 'Date', 'Reply-To', 'Mail-Reply-To', 'Mail-Followup-To', 'Message-ID', 'References', 'In-Reply-To']

def parse_attachment(message_part):
    """Return the attachment data as an object, if this part is indeed an attachment"""

    content_disposition = message_part.get("Content-Disposition", None)
    if content_disposition:
        dispositions = content_disposition.strip().split(";")
        if content_disposition and bool(dispositions[0].lower() == "attachment" or dispositions[0].lower() == "inline"):

            attachment = {}
            file_data = message_part.get_payload(decode=True)
            attachment['data'] = StringIO(file_data)
            attachment['content_type'] = message_part.get_content_type()
            attachment['size'] = len(file_data)

            for param in dispositions[1:]:
                name,value = param.split("=")
                name = name.lower().lstrip().rstrip()

                if name == "filename":
                    attachment['name'] = value.lstrip().rstrip()
                elif name == "create-date":
                    attachment['create_date'] = value.lstrip().rstrip() # this is a string, not a datetime (etc.) value
                elif name == "modification-date":
                    attachment['mod_date'] = value.lstrip().rstrip() # string
                elif name == "read-date":
                    attachment['read_date'] = value.lstrip().rstrip() # string
            return attachment

def get_header_component (msgobj, header_key):
    """Get the header component designated by the given key, decode it, and return it as an utf-8 string"""

    result = None
    try:
        decodefrag = decode_header(msgobj[header_key])
        fragments = []
        for s, enc in decodefrag:
            if s:
                if enc:
                    s = unicode(s, enc).encode(unicode_encoding, 'replace')
                fragments.append(s)
        if len(fragments) > 0:
            result = ''.join(fragments)
    except KeyError:
        pass
    return result

def parse(content):
    """Parse the content string of an email message and return a dict of the parts"""

    p = EmailParser()
    msgobj = p.parsestr(content)

    msgheaders = {}
    for header_key in header_parts:
        header_val = get_header_component (msgobj, header_key)
        if header_val and header_val != 'None':
            msgheaders[header_key] = header_val

    attachments = []
    body = None
    html = None
    for part in msgobj.walk():
        attachment = parse_attachment(part)
        if attachment:
            attachments.append(attachment)
        elif part.get_content_type() == "text/plain":
            if body is None:
                body = ""
            body += unicode(
                part.get_payload(decode=True),
                unicode_encoding if part.get_content_charset() is None else part.get_content_charset(),
                'replace'
            ).encode(unicode_encoding,'replace')
        elif part.get_content_type() == "text/html":
            if html is None:
                html = ""
            html += unicode(
                part.get_payload(decode=True),
                unicode_encoding if part.get_content_charset() is None else part.get_content_charset(),
                'replace'
            ).encode(unicode_encoding,'replace')
    return {
        'headers' : msgheaders,
        'body' : body,
        'html' : html,
        'attachments': attachments,
    }

