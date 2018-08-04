import os
import subprocess
import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email import encoders
from email.header import Header

# imap server settings
# SMTP Server which this program will receive from
SMTPServer = 'smtp.xxx.com'
IMAPServer = 'imap.xxx.com'         # IMAP Server which this program will send to
user = 'xxx@xxx.com'     # Your email address
passwd = 'xxxxxxx'            # Your email password
# The email address that send to this program.If the sender not match to
# this address, the command will be ignored.
master = 'xxx@xxx.com'

eserver = imaplib.IMAP4(host=IMAPServer)
eserver.login(user, passwd)
print("Login successfully!")

# Get current system information


def GetSysInfo():
    uptime = subprocess.getoutput('uptime')
    cpustat = subprocess.getoutput("dstat --tclmn --nocolor 1 5")
    cpuinfo = subprocess.getoutput('lscpu')
    Temp = subprocess.getoutput('cat /sys/class/thermal/thermal_zone0/temp')
    Tempfl = float(Temp) / 1000
    Temp = "Temperature:\n%f ℃" % (Tempfl)
    return 'Uptime:' + uptime + '\nCPU Stat:' + \
        cpustat + '\n' + cpuinfo + '\n' + Temp

# Get recent message


def GetRecentEmail():
    eserver.select()
    type, data = eserver.search(None, 'Recent')
    if data[0] == b'':
        return
    else:
        newlist = data[0].split()
        type, data = eserver.fetch(newlist[0], '(RFC822)')
        msg = email.message_from_string(data[0][1].decode('utf-8'))
        frm = msg.get('From')
        print(frm)
        frmdec = email.header.decode_header(frm)[2][0]
        if master in str(frmdec):
            sub = msg.get('Subject')
            title = email.header.decode_header(sub)[0][0]
            print(title)
            return title
        else:
            print('Sender authentication failed, instruction was intercepted')
            return


def SendEmail(subject, msgstr):
    msg = MIMEText(msgstr, 'plain', 'utf-8')
    msg['Form'] = user
    msg['To'] = master
    msg['Subject'] = subject
    try:
        sser = smtplib.SMTP(SMTPServer)
        sser.login(user, passwd)
        print('Login successfully!')
        sser.sendmail(user, [master], msg.as_string())
        print('Processed successfully')
    except smtplib.SMTPException as e:
        print(e)


def ListenEmail():
    stat = None
    try:
        stat = GetRecentEmail()
    except BaseException:
        print("Failed to get")
    if stat is None:
        print(time.ctime())
        print('Failed to receive instructions, pending...')
    else:
        print('Received instructions, processing...')
        cmd = stat[0:5]
        print(cmd)
        if cmd == 'state':
            print('Checking server status...')
            msgstr = GetSysInfo()
            msgstr = msgstr.replace('\x1b[0;0m', '').replace('\x1b[7l', '')
            print(msgstr)
            title = 'Server status %s' % time.ctime()
            SendEmail(title, msgstr)
        elif cmd == 'comnd':
            syscmd = stat[6:len(stat)]
            print(syscmd)
            status = subprocess.getoutput('uptime')
            title = 'Command executed successfully!%s' % syscmd
            msgstr = 'Executed %s command,Return:\n%s' % (msgstr, status)
            SendEmail(title, msgstr)
        else:
            print('Instruction identification error')


def main():
    if os.getuid() != 0:
        print("Need root privileges.")
        exit(1)
    while True:
        try:
            ListenEmail()
            time.sleep(5)
        except BaseException:
            print("Something went wrong")


if __name__ == '__main__':
    main()
