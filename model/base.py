#coding:utf-8
import tornado.web
import sys
import torndb
import subprocess
import datetime,time
import os,re,struct
import signal
import socket,hashlib
from tornado import iostream
from tornado import ioloop
from lib2to3.fixer_util import String
from macpath import split
from __builtin__ import int


class BaseHandler(tornado.web.RequestHandler):
    
    
    def initialize(self):
        
        self.classname = self.__class__.__name__
        self.user_header = self.get_secure_cookie('user', None)
        
    def get_current_user(self):
        return self.get_secure_cookie('user')
        
        
    @property  
    def db(self):
        db = torndb.Connection('127.0.0.1', 'devops', user='root', password='')
        return db
    
    def TIMEOUT_COMMAND(self, command, timeout):
        
        '''call shell-command and either return its output or kill it 
        if it doesn't normally exit within timeout seconds and return None'''
        
        time_start = datetime.datetime.now()
        process = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
        while process.poll() is None:
            time.sleep(0.2)
            time_now = datetime.datetime.now()
            if (time_now - time_start).seconds > timeout:
                os.kill(process.pid,signal.SIGKILL)
                os.waitpid(-1,os.WNOHANG)
                return "False error timeout"
        return process.stdout.read()
    
    def get_update(self, type, clecs, proj):
        '''
            get update pack list
        '''
        
        os.system(("ssh -p 9921 -i /home/deploy/.ssh/deploy_rsa deploy@x.x.x.x ls -lt --time-style=full-iso /data/update_dir/ | awk  '$NF ~ /^%s_%s_[0-9].*_%s/{print $6,$7,$NF}' | sed 's/\.[0]* / /' > .update_list") % (proj,type,clecs) )

        
        update = []

        try:
            for line in open(".update_list"):
                line=line.strip('\n')
                ver = re.findall(r".*_.*_([0-9].*)_.*",line[20:])
                update_info = {"ver":ver,"date":line[0:19],"file":line[20:]}
                update.append(update_info)
        except:
            return sys.exc_info()[0]

        return update
    
    def get_page_limit(self, nowPage, pagenum):
        
        row = pagenum * (nowPage - 1)
        
        return row
    

    

class SocketHandler(BaseHandler):


    def send_socket(self, type=1, id='1', ipaddr='1', command=''):
         
        if not type:
            return False 
        
        self.type = type
        self.job_id = id
        self.ipaddr = ipaddr
        self.command = command
        # len(key) = 32 
        self.key = 'xxxxxxxxxxxxxxxxxxxxxxxxxxx'
        
        HOST = ipaddr    # The remote host  
        PORT = 8742           # The port as used by the server  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)     
        self.stream = iostream.IOStream(s)
        self.stream.set_close_callback(self.auth_close)
        
        try:
            self.stream.connect((HOST, PORT), self.auth_request)
            
        except:
            return False
        
    def auth_close(self):
        self.stream.closed()
        
        
    def auth_request(self):
        def auth_send(data):

            md5_hash = hashlib.md5(self.key + data[0:20]).hexdigest()
            self.stream.write(md5_hash[10:], self.auth_ok)
        
        
        self.stream.read_bytes(30, auth_send)
        
    
    def auth_ok(self):
        
        self.stream.write(struct.pack('!H', self.type), self.send_data)
        
    
    def send_data(self):

        
        if self.type == 1:
            # to binary
            command_len = len(self.command)
            str_pack = "!II%ds" % (command_len)
            self.stream.write(struct.pack(str_pack, self.job_id, command_len, self.command.encode('utf-8')))
            self.stream.read_bytes(6, self.status_request)
                 
        elif self.type == 2:
            
            
            self.stream.closed()
            self.db.execute("update ops_server set server_last_report=UNIX_TIMESTAMP() where server_wan_ip=%s", self.ipaddr)
            
        elif self.type == 3:
            command_len = len(self.command)
            str_pack = "!I%ds" % (command_len)
            self.stream.write(struct.pack(str_pack, command_len, self.command.encode('utf-8')))
            info = self.read_char()
        
    def status_request(self, data):
        
        running_state,recive = struct.unpack('!HI', data)
        
        #print running_state
        self.db.execute("update ops_joblist set joblist_status=4,joblist_start_time=UNIX_TIMESTAMP() where id=%s", self.job_id)
        
        
    def read_char(self):
        def read_char_val(data):
            char_len, = struct.unpack('!I',data)
            self.stream.read_bytes(char_len, self.area_request)
        
        self.stream.read_bytes(4, read_char_val)
        

    def area_request(self, data):
        
        print data
#         area_state = 1 if data.split(',')[1] == 'True' else 0
#         area_install = 1 if data.split(',')[0] == 'True' else 0
        area_install = data.split(':')[0]
        area_state = data.split(':')[1]
        area_ver = data.split(':')[2]
         
        self.db.execute("update ops_area set area_state=%s,area_install=%s,area_version=%s where id=%s", area_state, area_install, area_ver, self.job_id)
        
        
          
        
        
        
        
        
        
        
        
        
        
    
        