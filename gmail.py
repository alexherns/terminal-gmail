#!/usr/bin/env python2.7
import smtplib, getpass, argparse, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser

def message_from_prompt():
    """Generates MIMEText message from user input at prompt""" 
    username= raw_input('Username: ')
    fromaddr= username+'@gmail.com'
    toaddrs= raw_input('Destination: ')
    subject= raw_input('Subject: ')
    body= raw_input('Message: ')
    msg= MIMEText(body)
    msg['Subject']= subject
    msg['From']= fromaddr
    msg['To']= toaddrs
    return msg

def message_from_file(fhandle):
    """Generates MIMEText message from MIME-formatted text file"""
    msg= email.message_from_file(fhandle)
    return msg

def message_from_args(args):
    """Generates MIMEText message from terminal arguments"""
    username= args.username
    body= args.body
    fromaddr= username+'@'+args.client+'.com'
    toaddrs= args.targetaddress
    subject= args.subject
    msg= MIMEText(body)
    msg['Subject']= subject
    msg['From']= fromaddr
    msg['To']= toaddrs
    return msg

def transfer_msg_info(source_msg, dest_msg):
    """Transfers message subject and addresses to new message"""
    dest_msg['subject']= source_msg['subject']
    dest_msg['from']= source_msg['from']
    dest_msg['to']= source_msg['to']
    return dest_msg

def build_attachment(atttachment_path):
    """Generates MIMEText attachment-like message from file path"""
    fhandle= open(atttachment_path, 'rb')
    attachment= MIMEText(fhandle.read())
    fhandle.close()
    attachment.add_header('Content-Disposition', 'attachment',
            filename=atttachment_path)
    return attachment

def send_gmail(username, password, msg):
    """Sends a MIME message using gmail"""

    #Yank addresses and username from MIMEText message
    toaddrs= msg['to']
    fromaddr= msg['from']

    # The actual mail send
    print 'Connecting to server...'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    print 'Logging in...'
    server.login(username,password)
    print 'Sending message...'
    server.sendmail(fromaddr, toaddrs, msg.as_string())
    print 'Finished!'
    server.quit()



def main(args):
    """Main script for sending gmail messages"""

    outer= MIMEMultipart()
    # Credentials (if needed)
    if args.verbose:
        msg= message_from_prompt()
    elif args.formatfile:
        msg= message_from_file(open(args.formatfile))
    else:
        msg= message_from_args(args)
    outer.attach(msg)
    outer= transfer_msg_info(msg, outer)
    username= outer['from'].split('@')[0]

    #Password from argument or getpass
    if args.password:
        password= args.password
    else:
        password= getpass.getpass()
    
    #Attach files if requested
    if args.attachment:
        outer.attach(build_attachment(args.attachment))

    send_gmail(username, password, outer)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''Simple command line parser
        for sending email''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    parser.add_argument('-h', action='help', 
            help='show this help message and exit')
    parser.add_argument('-v', action='store_true', 
            help='verbose, prompt builds message', dest= 'verbose')
    parser.add_argument('-u', type=str, default='alexherns',
            help='username', dest= 'username')
    parser.add_argument('-p', type=str, 
            help='password', dest= 'password')
    parser.add_argument('-c', type=str,
            help='email client', default='gmail',
            dest= 'client')
    parser.add_argument('-t', type=str,
            help='target email address', dest='targetaddress')
    parser.add_argument('-s', type=str,
            help='email subject', dest='subject')
    parser.add_argument('-b', type=str,
            help='email message body', dest='body')
    parser.add_argument('-f', type=str,
            help='generate email from file',
            dest='formatfile')
    parser.add_argument('-a', type=str,
            help='attach a file', dest='attachment')

    args= parser.parse_args()

    main(args)
