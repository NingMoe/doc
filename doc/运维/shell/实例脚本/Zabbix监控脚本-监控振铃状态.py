#-*- coding:gbk -*-
#�ű����ڼ������״̬��������״̬��Ϣ��zabbix����������Ҫ���zabbixģ�壬���ӹ����жϴ�����
# �汾3 ����ÿ�춨ʱ�Զ���������Ĺ��� �޸�����ʧ��bug ����һЩ����
import urllib2,json
import os,sys
import time,datetime
import serial
import getopt

#������������ip��ַ
ip = "127.0.0.1"
#������Ҫ��������url��ַ
url = "http://%s:1234/Server/status" % ip
#��������Ŀ��ƴ��ں�
triggerComPort = "COM56"
#��������������������ķ�ֵ
normalThreshold = 10
#����zabbix��������ַ
zabbixserver = '172.16.0.1'
#����zabbix��������Ķ˿ڣ�����zabbix_sender��������
zabbixport = '10051'
#zabbix_sender�����·��
zabbix_sender_bin = r'C:\zabbix_agent\bin\win32/zabbix_sender.exe'
#���ڷ��͵�zabbix�������ļ�·�� --input-fileѡ��֮��
datacachefile = r'C:\zabbix_agent\trigger_status_%s_1234.txt' % ip
#����zabbix web gui�����õ���������
HOST='Trigger02'

#������������������ݿڵ��ַ���
alive_information = "order:noActive"
#����������������ݿڽ��յ�����1
order1 = "order:close1"


#������־���������ڴ��һЩ��־���򵥵���python�Դ���loggingģ�飬������Ҫ��������־��Ϣ����־�ļ�����
def logger(info,logfile):
    import logging  
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s    %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logfile,
                        filemode='a')
    logging.debug(info)

#���巢�ʼ��ĺ��������ڵ�����Ŀ����������ڷ�ֵ��ʱ���Զ������ʼ��������ǿ�ӵ���������
def information(num):
    import smtplib
    import email.utils
    from email.message import Message
    
    #�ʼ��ķ��͵�ַ����Ҫ�Զ���
    from_addr = "xxxxx@163.com"
    #�ʼ��Ľ��յ�ַ����Ҫ�Զ���
    to_addr = "xxxxx@sabc.net"
    #����
    subject = "TRIGGER ERROR!!!"
    #smtp server��Ҫ�Զ���
    smtpserver = "smtp.163.com"
    #�û�����һ����ʼ����͵�ַ��ͬ
    username = from_addr
    #��½����
    password = "1234567789"
    #��ȡ���ڵ��¼� RFC 2822��׼
    current_time = email.utils.formatdate(time.time(),True)
    #�ʼ����͵����ݣ�����д��������������������ģ����ݿ����Զ���
    content = """This is a mail from trigger
    You should handle trigger server manually
    The SIM available number is : %s
    The trigger is 192.168.1.12
    """ % num

    #����һ������Message����
    Smessage = Message()
    #ָ������
    Smessage["Subject"] = subject
    #�ƶ�������
    Smessage["From"] = from_addr
    #ָ���ռ���
    Smessage["To"]= to_addr
    #ָ������
    #Smessage["Cc"] = cc_addr
    #��������
    Smessage.set_payload(content+current_time)
    #�����ַ������͵� ��ʽ����Ϣ
    msg = Smessage.as_string()

    try:
        #����smtp������
        sm = smtplib.SMTP(smtpserver)
    #�����쳣SMTPConnectError
    except SMTPConnectError as e:
        #��ӡ�쳣���� �쳣��Ϣ
        print SMTPConnectError,e
        #��һ�쳣��Ϣ
        message = "SMTPConnectError,%s" % e
        #��¼�쳣��Ϣ������logger����
        logger(message,r'C:\Users\admin\Desktop\debug.log')
        exit()
    #���û���κ��쳣
    else:
        try:
            #���Ե�½
            sm.login(username,password)
        #������½�쳣 SMTPHeloError,SMTPAuthenticationError,SMTPException
        except (SMTPHeloError,SMTPAuthenticationError,SMTPException) as e:
            #�����쳣��Ϣ 
            message = "SMTPHeloError,SMTPAuthenticationError,SMTPException,%s" % e
            #��¼�쳣��Ϣ
            logger(message,r'C:\Users\admin\Desktop\debug.log')
            exit()
        #�����¼����
        else:
            #ִ�з����ʼ�����
            sm.sendmail(from_addr,to_addr,msg)
    #��Ϣ5����
    time.sleep(5)
    #�����ʼ����ͳɹ�����Ϣ
    message = "mail send successfully!!!"
    #��¼�ʼ����ͳɹ���Ϣ
    logger(message,r'C:\Users\admin\Desktop\debug.log')
    #�˳��ʼ�������
    sm.quit()

#�������������������ڷ��ֹ��ϵ�һ������
def restart_program():
    #�������������Ϣ
    print  "���������С�����"
    #����kill���������
    kill_java = r"taskkill /F /IM java.exe"
    #ִ��kill��������
    os.system(kill_java)
    #��������·��
    filename = r"C:\Users\admin\Desktop\start.bat.lnk"
    #�����������������
    cmd = r'cmd /k "start %s' % filename
    #ִ�г�������
    os.popen(cmd)
    return


#����һ���࣬���ڷ���zabbix�����ݱ�׼����
class Metric(object):
    #��ʼ�� �������� �� ֵ 
    def __init__(self, host, key, value):
	    self.host = host
	    self.key = key
	    self.value = value
    #����һ���̵�̫����	    
    def __iter__(self):
            return iter([self.host,self.key,self.value])

#����״̬���� ����ͳ��״̬ �������ݵ�zabbix server	����Ϊ������ ��װ��������	
def status(func_name):
    #����״̬ͳ�ƺ���
    def status_count():
        #��ʼ������״̬��������ֵΪ0
        error=normal=total=failed_count=success_count=wait_count=doing_count = 0
        
        try:
            #���Դ򿪼��url
            data_init = urllib2.urlopen(url)
            #��ȡurl����
            data = data_init.read()
        #��url�����쳣
        except:
            try:
                #�����쳣��Ϣ���쳣����
                message = "CODE: %s, Open the url failed!" % data_init.code
            #����UnboundLocalError�쳣����http�쳣
            except UnboundLocalError:
                #���������쳣��Ϣ
                message = "UnboundLocalError: local variable 'data_init' referenced before assignment"
                sys.exit(3)

        #��json�������ݣ�ת��Ϊ�ֵ�����
        status_dict = json.loads(data)
        #�����ֵ��е����д���
        for port in status_dict["info"]["com"].keys():
                #�������״̬Ϊerror ����error�Լ�1
                if status_dict["info"]["com"][port]["error"]:error += 1
                #����normal�Լ�1
                else:
                    normal += 1
                #ÿ����һ��total�Լ�1
                total += 1
        #�õ���ֵ��ȥwindows���Դ���com1���������������
        total -= 2
        error -= 2
        #ͳ������״̬ forѭ������
        for id in status_dict['info']['task'].keys():
                #���״̬Ϊfailed����ô����failed_count�Լ�1
                if status_dict['info']['task'][id]['callStatus'] == 'failed':failed_count += 1
                #���״̬Ϊsuccess����ô����success_count�Լ�1
                if status_dict['info']['task'][id]['callStatus'] == 'success':success_count += 1
                #���״̬Ϊwait����ô����wait_count�Լ�1
                if status_dict['info']['task'][id]['callStatus'] == 'wait':wait_count += 1
                #���״̬Ϊdoing����ô����doing_count�Լ�1
                if status_dict['info']['task'][id]['callStatus'] == 'doing':doing_count += 1
        #���ظ���״̬��ֵ 
        return error,normal,total,failed_count,success_count,wait_count,doing_count
    #��������zabbix�������ļ� --input-fileѡ��֮��
    def write2file():
        #�����ֵ�ļ�ֵ ����һ���б� ������һһ��Ӧ
        namelist = ['Error','Available','Total','Failed','Success','Waiting','Doing']
        #����״̬�ֵ�
        datadict = dict(zip(namelist,status_count()))
        #�������ļ�
        f = open(datacachefile,'w')
        #����״̬�ֵ䣬����ÿһ�е������ַ���
        for key,value in datadict.items():
            #����Ҫд���ļ�ÿһ�е��ַ���
            datastr = '\t'.join(Metric(HOST,('trigger.status[%s]' % key),str(value)))+'\n'
            #д���ļ�
            f.writelines(datastr)
        #ˢ��
        f.flush()
        #�ر��ļ�
        f.close()
        #���������ֵ�
        return datadict
    #���巢�͵�zabbix server�ĺ���
    def send2zabbix():
        #���͵�zabbix server������
        cmd = "%s --zabbix-server %s --port %s --input-file %s "  % (zabbix_sender_bin,zabbixserver,zabbixport,datacachefile)
        #ִ������
        os.system(cmd)
    #����ִ�к��� ��������Ķ��庯��
    def execute():
        #ִ�к��� ����״̬�ֵ�
        datadict = write2file()
        #���͵�zabbix server
        send2zabbix()
        #����
        return func_name(datadict)
    #����execute�հ�����
    return execute
#���庯��װ����
@status
#���Ӻ��� ����״̬�ֵ�
def r2d(datadict):
    return datadict

#��������ϵͳ�ĺ��������ڷ������ϵڶ�������������������Զ�����֮�� ��������
def soft_restart_system():
    #�������ʱ�������־�ļ�
    logfile = r'C:\Users\admin\Desktop\logs_%s.txt' % time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())
    logger("���棺 ׼��������ϵͳ",logfile)
    print "��ʼ������ϵͳ������"
    for i in range(5,-1,-1):
        print "����ʱ����   %s " % str(i)
    #����ϵͳ��������
    restart_cmd = r"shutdown /r /t 00"
    #ִ��ϵͳ��������
    os.system(restart_cmd)
    return

#�����������壬���ڷ������ϵ���������    
def restart_trigger():
    #���������ƴ����Ǵ򿪵�
    if ser.isOpen():
        #��Ϣ5��
        time.sleep(5)
        #�򴮿ڷ��������������1
        ser.write(order1)
        #�������������������
        print "�������������С�����"
    #�������û�д�
    else:
        #���������Ϣ
        message = "������������ݿڴ�ʧ�ܣ�"
        #���������Ϣ
        print message
        #����¼����־
        logger(message,r'C:\Users\admin\Desktop\debug.log')
        exit()

    
    
#��������������Ƿ�������麯�������ں����������ͨ��
def alive_check():
    #��������Ǵ򿪵�
    if ser.isOpen():
        #���ͼ����Ϣ
        ser.write(alive_information)
        #�����������ѷ���
        print "���������ݿڼ��: ͨ������"
    #����
    else:
        #���������Ϣ
        message = "������������ݿڴ�ʧ��"
        #��ӡ������Ϣ
        print message
        #��¼������Ϣ
        logger(message,r'C:\Users\admin\Desktop\debug.log')
        exit()

#����ոտ����������ȴ�50�룬�ȴ�java���������������
time.sleep(50)

try:
    #���Դ��������������
    ser = serial.Serial(triggerComPort,115200)
    #�򿪳ɹ� ��ӡ�ɹ���Ϣ
    print "������������ݿڴ򿪳ɹ�"
    #�������״̬�ǹرյ�
    if ser.closed:
        #�ٴ�ִ�д�
        ser = serial.Serial(triggerComPort,115200)
#���ڴ򿪷����쳣
except:
    #�����쳣��Ϣ
    message = "������������ݿڴ�ʧ��"
    #��ӡ�쳣��Ϣ
    print message
    #��¼�쳣��Ϣ
    logger(message,r'C:\Users\admin\Desktop\debug.log')
    #�����ʼ�֪ͨ���˹�����
    information("0")
    exit()

#��ʼ������������ѭ������
while True:
    #��ʼ�����ϴ�����Ϊ0
    RestartTriggerTag=0
    #��ȡ״̬�ֵ�
    datadict = r2d()
    #����״̬��ӡ��ֵ ����console�۲�ʵʱ״̬
    record_count = "���õ�SIM������: " + str(datadict['Available']) + " ʧ�ܵ�����: " + str(datadict['Failed']) \
                   + " �ɹ�������: " + str(datadict['Success']) + " �Ŷӵ�����: " + str(datadict['Waiting']) \
                   + " ���ڴ��������: " + str(datadict['Doing'])
    #��ӡ��Ϣ
    print record_count
    #ѭ���жϿ�������С���趨�ķ�ֵ
    while datadict['Available'] <= normalThreshold:
        #�����û������������
        if RestartTriggerTag < 1:
            #��������
            restart_trigger()
            #����������Ǽ�1
            RestartTriggerTag += 1
            #��¼��־
            logger("���ؾ���: ���������С�����",r'C:\Users\admin\Desktop\debug.log')
            #��Ϣ30�� �ȴ������������
            time.sleep(30)
            #���»�ȡ״̬����
            datadict = r2d()
            #��ӡ״̬
            print "�����������",RestartTriggerTag,datadict['Available']
        #������������壬��û���������򣬿���������Ȼ���ڷ�ֵ
        #ȥ�������������
        else:
            #��¼��־ ��Ҫ������
            logger("���棺 ������ϵͳ",r'C:\Users\admin\Desktop\debug.log')
            information(datadict['Available'])
            #��������ϵͳ
            soft_restart_system()
    #������������ �����趨��ֵ��
    else:
        #������߱����һ��Ϊ1 ����ִ�й�
        if RestartTriggerTag == 1:
            #����ָ��ɹ���Ϣ
            message = "�����������Ѿ��ɹ����һָ���"
            #��ӡ��Ϣ
            print message
            #��¼��־
            logger(message,r'C:\Users\admin\Desktop\debug.log')
            #�Ƴ���������ļ� Ϊ��ִ������һ�ֹ��ϴ����0��ʼ
            os.remove(r"C:\Users\admin\Desktop\local_com_checks.ini")
    #�����ʼ������������ü��
    #print "Begain checking alive..."
    #ִ�м�⺯�� �����������ȡ���� ����û���κ��ж�
    alive_check()
    #��ʱ��������
    current_time_in_day =  datetime.datetime.now()
    if current_time_in_day.hour == 1 and current_time_in_day.minute == 10 and current_time_in_day.second < 45:
        restart_trigger()
        soft_restart_system()
    print "��ǰʱ��: %s \n" % current_time_in_day
    #��Ϣʮ�� ÿ10��ѭ��һ��
    time.sleep(10)

