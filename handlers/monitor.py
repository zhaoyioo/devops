#coding:utf-8

from model.base import *
from multiprocessing.dummy import Pool as ThreadPool
from datetime import date
import new
from tornado.escape import json_encode



class ServerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        server_list = self.db.query("select * from ops_server left join ops_room on ops_server.server_room=ops_room.room_id")
        
        ##loop check status
        for i in server_list:
            ServerSocket(i['server_wan_ip'])
        
        self.render('monitor/server.html', server_list = server_list)
        
class ServerSocket(SocketHandler):
    
    def __init__(self, ip):
        
        self.send_socket(type=2, ipaddr=ip)
        
        
        
class GetServerStatusHandler(SocketHandler):
            
    @tornado.web.authenticated
    def post(self):
         
        server_id = self.get_argument('server_id', None)
        server_last_report = self.db.get("select server_last_report from ops_server where server_id=%s",server_id)
         
        if server_last_report['server_last_report']:
           
            if server_last_report['server_last_report'] != '' and (time.time() - server_last_report['server_last_report']) < 60 :
                
                self.write('1')
            else:
                self.write('0')
            

class GetAreaStatusHandler(SocketHandler):
    
    @tornado.web.authenticated
    def post(self):
        
        id = self.get_argument('id', None)
        
        area_info = self.db.get("select area_state,area_install,area_version from ops_area where id=%s", id)

        area_dict = {}
        
        area_dict['area_state'] = area_info['area_state']
        area_dict['area_install'] = area_info['area_install']
        area_dict['area_version'] = area_info['area_version']
        
        self.write(json_encode(area_dict))
            
            
        
            
            


        
        