import os
import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email import encoders
from email.header import Header
               
#imap server settings
user=open('./config/username').read().splitlines()[0]
pass_=open('./config/password').read().splitlines()[0]
master=open('./config/master').read().splitlines()[0]

eserver=imaplib.IMAP4(host="imap.126.com")
eserver.login(user,pass_)

print("Login successfully!")

mainEA=[master]

#Get current system information
def GetUptime():
    os.system("uptime > upo")
    tmp=open("./upo")
    Up=tmp.read()
    tmp.close()
    os.system('rm -f ./upo')
    return Up
    
def GetCPU():
    os.system("dstat -tclmn --nocolor 1 5 > cpu")
    tmp=open("./cpu")
    Cpu=tmp.read()
    tmp.close()
    os.system("lscpu > cpu")
    tmp=open("./cpu")
    Up=tmp.read()
    tmp.close()
    os.system('rm -f ./cpu')
    return Cpu+'\n'+Up

def GetTemp():
    tmp=open("/sys/class/thermal/thermal_zone0/temp")
    Temp=tmp.read()
    Tempfl=float(Temp)/1000
    Temp="Temperature:\n%f"%(Tempfl)
    tmp.close()
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
            msgstr='UPTIME:\n'+GetUptime()+'\nCPU:\n'+GetCPU()+'\n'+GetTemp()
            msgstr=msgstr.replace('\x1b[0;0m','').replace('\x1b[7l','')
            print(msgstr)
            msg=[]
            msg=MIMEText(msgstr,'plain','utf-8')
            msg['Form']='{}'.format(user)
            msg['To']=','.join(mainEA)
            title='Server status %s' % str(time.asctime(time.localtime(time.time())))
            msg['Subject']=title
            try:
                sser=smtplib.SMTP('smtp.126.com')
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
                sser=smtplib.SMTP('smtp.126.com')
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
                sser=smtplib.SMTP('smtp.126.com')
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
while True:
    try:
        ListenEmail()
    except BaseException:
        print("Something went wrong")
