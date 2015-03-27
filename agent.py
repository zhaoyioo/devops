#coding:utf-8
'''
______________________________________________
_______________#########_______________________
______________############_____________________
______________#############____________________
_____________##__###########___________________
____________###__######_#####__________________
____________###_#######___####_________________
___________###__##########_####________________
__________####__###########_####_______________
________#####___###########__#####_____________
_______######___###_########___#####___________
_______#####___###___########___######_________
______######___###__###########___######_______
_____######___####_##############__######______
____#######__#####################_#######_____
____#######__##############################____
___#######__######_#################_#######___
___#######__######_######_#########___######___
___#######____##__######___######_____######___
___#######________######____#####_____#####____
____######________#####_____#####_____####_____
_____#####________####______#####_____###______
______#####______;###________###______#________
________##_______####________####______________

    Handlers: index 
    author: K  
    mail: 13620459@qq.com

'''

import socket,sys,os
import time
import hashlib
import struct,subprocess
import urllib,urllib2
import threading
import random

class Main(threading.Thread):
    
    slef.s = s
    slef.cs = cs
    self.address = address

    def __init__(self):
        threading.Thread.__init__(self)
        
        #32 bit md5
        key = 'xxxx'
        
        self.s=socket.socket()
        self.s.bind(('0.0.0.0',8888))
        self.s.listen(1)
        
        try:
            while 1:
                self.cs, self.address = self.s.accept()
                self.cs.settimeout(5)
                print 'got connected from',self.address
                try:
                    md5_hash = hashlib.md5(("%s%s") % (time.time(),random.randint(0,100))).hexdigest()
                    self.cs.send(md5_hash[0:30])
                    check_code=self.cs.recv(22)
                    #print check_code
                    if check_code == hashlib.md5(key + md5_hash[0:20]).hexdigest()[10:]:
                        print 'ok'
                        
                        type = self.read_ShortInt()
                        
                        if not isinstance(type, int):
                           self.cs.close()                        
                        
                        if type == 1:
                            
                            joblist_id = self.read_Int()
                            command = self.read_Char()
                            self.report_status(joblist_id)
                            self.game(joblist_id, command)
                        
                        elif type == 2:
                            pass
                            #self.cs.send(struct.pack('!H',1))
                            
                        elif type == 3:
                            command = self.read_Char()
                            get_retrun = str(self.get_info(command))
                            return_len = len(get_retrun)
                            str_pack = "!I%ds" % (return_len)
                            self.cs.send(struct.pack(str_pack, return_len, get_retrun.encode('utf-8')))
                       

                        self.cs.close()
                    else:
                        self.cs.close()
                            
                except socket.timeout:
                    print 'timeout'
                    self.cs.close()
                    
        except KeyboardInterrupt:
            print 'Ctrl + c ,close'
            self.cs.close()
            sys.exit()      

        
    def read_ShortInt(self):
        try:
            sint, = struct.unpack('!H',self.cs.recv(2))
            return sint
        except:
            return None
        
    def read_Int(self):
        try:
            int, = struct.unpack('!I',self.cs.recv(4))
            return int
        except:
            return None
            
    def read_Char(self):
        try:
            char_len, = struct.unpack('!I',self.cs.recv(4))
            char_str = "!%ds" % (char_len)
            char, = struct.unpack(char_str,self.cs.recv(char_len))
            return char
        except:
            return None
     
    def game(self, joblist_id ,command):
    
        command_dict = self.toDict(command)
            
        if command_dict['-p'] == 'yxgj':
            game_comm = "python yxgj.py %s" % (command.replace(':',' '))
            game_run = self.Commands(game_comm)
                
            if game_run.strip() != 'True':
                self.report_http(joblist_id, 2 , game_run.strip())
            else:
                self.report_http(joblist_id, 1 , game_run.strip())
        

    def get_info(self,command):
        
        get_dict = self.toDict(command)
        
        if get_dict['-get'] == 'area':
        
            if get_dict['-p'] == 'yxgj':
                game_path = '/data/gameserver/yxgj/S%s' % (get_dict['-s'])
            
                if os.path.exists(game_path):
                
                    get_comm = "python yxgj.py -p yxgj -t server -a status -s %s -c 888 -v 0 -h 127.0.0.1" % (get_dict['-s'])
                    get_run = self.Commands(get_comm)
                    
                    if get_run.strip() == 'True':
                        server_state = 1
                    else:
                        server_state = 0
                    
                    ver_file = "%s/version" % (game_path)
                    
                    try:
                        fsock = open(ver_file, "r")
                        server_ver = int(fsock.readline())
                    except IOError:
                        server_ver =  0
                        
                    return '1:%d:%d' % (server_state, server_ver)

                else:
                    return '0:0:0'
                
            
        
    
    def area_status(self, game_name, area_id):
        pass
        
    
    def update(self):
        pass
        
    def report_status(self, joblist_id):
        
        running_state = struct.pack('!HI', 4, joblist_id)
        self.cs.send(running_state)
       
    def Commands(self, command):
    
        process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
        return process.stdout.read()
        
    def report_http(self, jid, status, log):
        
        post_dic = {
            'jid':jid,
            'status':status,
            'log':log
        }
        
        post_data = urllib.urlencode(post_dic);
        
        try:
            req = urllib2.Request('http://test.zhaoyi.org/deploy/ReportJobHandler', post_data);
            req.add_header('Content-Type', "application/x-www-form-urlencoded");
            resp = urllib2.urlopen(req);
            #print resp
        except:
            pass
            
    def toDict(self, command):
        command_split = command.split(' ')
        dict = {}
        for i in command_split:
            temp_key = i.split(':')[0]
            temp_val = i.split(':')[1]
            dict[temp_key] = temp_val
        return dict

Main()        
    

