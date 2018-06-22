import os
import myconfig
import subprocess
import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
               
#imap server settings
user        = myconfig.emailname
pass_       = myconfig.emailpassword
master      = myconfig.receivefrom
IMAPServer  = myconfig.imapserver
SMTPServer  = myconfig.smtpserver

eserver=imaplib.IMAP4(host=IMAPServer)
eserver.login(user,pass_)

print("Login successfully!")

mainEA=[master]

#Get current system information
def GetUptime():
    return subprocess.getoutput('uptime')
    
def GetCPU():
    os.system("dstat -tclmn --nocolor 1 5 > cpu")
    tmp=open("./cpu")
    cpustat=tmp.read()
    tmp.close()
    os.system('rm -f ./cpu')
    cpuinfo=subprocess.getoutput('lscpu')
    return cpustat + '\n' + cpuinfo

def GetTemp():
    Temp=subprocess.getoutput('cat /sys/class/thermal/thermal_zone0/temp')
    Tempfl=float(Temp)/1000
    Temp="Temperature:\n%f ℃"%(Tempfl)
    return Temp
    
#Get recent message
def GetRecentEmail():
    eserver.select()
    type,data=eserver.search(None, 'Recent')
    if data[0]==b'':
        return 'none'
    else:
        newlist=data[0].split()
        type,data=eserver.fetch(newlist[0], '(RFC822)')
        msg=email.message_from_string(data[0][1].decode('utf-8')) 
        frm=msg.get('From')
        print(frm)
        frmdec=email.header.decode_header(frm)[2][0]
        if master in str(frmdec):
            sub=msg.get('Subject')
            title=email.header.decode_header(sub)[0][0]        
            print(title)
            return title
        else:
            print('Sender authentication failed, instruction was intercepted')
            return 'none'
        
def ListenEmail():
    stat='none'
    try:
        stat=GetRecentEmail()
    except BaseException:
        print("Failed to get")
    if stat=='none':
        print(time.asctime(time.localtime(time.time())))
        print('Failed to receive instructions, pending...')
        time.sleep(15)
    else:
        print('Received instructions, processing...')
        cmd=stat[0:5]
        print(cmd)
        if cmd=='state':
            print('Checking server status...')
            msgstr='UPTIME:\n'+GetUptime()+'\n\nCPU:\n'+GetCPU()+'\n\n'+GetTemp()
            msgstr=msgstr.replace('\x1b[0;0m','').replace('\x1b[7l','')
            print(msgstr)
            msg=[]
            msg=MIMEText(msgstr,'plain','utf-8')
            msg['Form']='{}'.format(user)
            msg['To']=','.join(mainEA)
            title='Server status %s' % str(time.asctime(time.localtime(time.time())))
            msg['Subject']=title
            try:
                sser=smtplib.SMTP(SMTPServer)
                sser.login(user,pass_)
                print('Login successfully!')
                sser.sendmail(user,mainEA,msg.as_string())
                print('Process successfully!')
                sser.close()
            except smtplib.SMTPException as e:
                print(e)
            time.sleep(5)
        elif cmd=='shutd':
            msg=[]
            msg=MIMEText(('Shutting down... %s' % str(time.asctime(time.localtime(time.time())))),'plain','utf-8')
            msg['Form']='{}'.format(user)
            msg['To']=','.join(mainEA)
            msg['Subject']='Server shutdown'
            try:
                sser=smtplib.SMTP(SMTPServer)
                sser.login(user,pass_)
                print('Login successfully!')
                sser.sendmail(user,mainEA,msg.as_string())
                print('Process successfully！')
            except smtplib.SMTPException as e:
                print(e)
            time.sleep(5)
            os.system('shutdown -h now')
        elif cmd=='comnd':
            syscmd=stat[6:len(stat)]
            print(syscmd)
            os.system(syscmd)
            msgstr='Command executed successfully!%s '%syscmd
            msg=[]
            msg=MIMEText(('Excuted %s command，time%s'%(msgstr,str(time.asctime(time.localtime(time.time()))))),'plain','utf-8')
            msg['Form']='{}'.format(user)
            msg['To']=','.join(mainEA)
            msg['Subject']='Excute command'
            try:
                sser=smtplib.SMTP(SMTPServer)
                sser.login(user,pass_)
                print('Login successfully!')
                sser.sendmail(user,mainEA,msg.as_string())
                print('Process successfully！')
            except smtplib.SMTPException as e:
                print(e)
            time.sleep(5)
        else:
            print('Instruction identification error')

#主程序
def main():
    if os.getuid() != 0:
        print("Need root privileges.")
        exit(1)

    while True:
        try:
            ListenEmail()
        except BaseException:
            print("Something went wrong")


if __name__ == '__main__' :
    main()
