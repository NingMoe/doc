    '''�����߿��Զ���һ������Ƶ������������һ��Ƶ��������Ϣ�����ж������Ƶ���Ķ����߶����յ���Ϣ��
	��������Ҳ���յ�һ����ֵ�������ֵ���յ���Ϣ�Ķ����ߵ�������
	������ֻ���յ�������ʼ���ĺ󷢲�������������Ϣ��
	֮ǰ��������Ϣ�أ��Ͳ������յ��ˡ�'''

#������̵ķ���
#!/usr/bin/python
#coding:utf-8

#��������
import redis  
r = redis.Redis(host='127.0.0.1',port='6379')#����redis
p = r.pubsub()  	    		#��������
p.subscribe('6379') #���ն��ĵ�����,���ĵ�Ƶ�� 

for item in p.listen(): #��ȡ���յ�����
    print item 
    if item['type'] == 'message':#�ж������Ƿ����û�����������   
        data = item['data']     #ȡ���û�Ҫ����������
        print data  #��ӡҪ����������

        if item['data'] == 'Q' or item['data'] == 'q':    
            break;  			    #�˳�����
p.unsubscribe('6379')#�ر�Ƶ��  
print 'ȡ������'

#�ͻ���
#!/usr/bin/py
#coding:utf-8
import redis  
r = redis.Redis(host='127.0.0.1',port=6379)#����redis
  
while True:  
    my_input = raw_input("�����뷢������:")#���뷢��������  
    r.publish('6379', my_input)#���͵���Ƶ��,����������  

    if my_input == 'Q' or my_input == 'q':  	    #�ж��û��Ƿ�Ҫ�˳�����
        print 'ֹͣ����'  
        break; 


#�������ķ���
#��������
#!/usr/bin/python
#coding:utf-8
import redis

class server(object):
    def __init__(self,ip='127.0.0.1',port=6379,sub='A'):
        self.ip = ip
        self.port = port
        self.connect = redis.Redis(host=self.ip,port=self.port)  #����redis
        self.sub = sub #����Ƶ��
    def se(self):
        spub = self.connect.pubsub()#�򿪶���
        spub.subscribe(self.sub)#��ʼ����
        spub.listen()#�û�����������
        return spub

x = server()
p = x.se()
for item in p.listen():				    #��ӡ���յ�������
    print item

#�ͻ���
#!/usr/bin/python
#coding:utf-8
import redis

class client(object):
    def __init__(self,ip='127.0.0.1',port=6379,pub='A'):
        self.ip = ip
        self.port = port
        self.connect = redis.Redis(host=self.ip,port=self.port)
        self.pub = pub		        #���ӵ�Ƶ��
    def cl(self,content):
        self.connect.publish(self.pub,content)#Ƶ��,���͵�����

x = client()
while True:
    my_input = raw_input('�����뷢�����ݣ�')	    #����������
    x.cl(my_input)

		
		