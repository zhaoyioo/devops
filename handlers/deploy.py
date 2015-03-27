#coding:utf-8

import json
from httplib import HTTPResponse
from model.base import *
from _bsddb import version
from _struct import pack_into
from __builtin__ import str

class PackHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        
        proj_list = self.db.query("select * from ops_proj")
        clecs_list = self.db.query("select * from ops_clecs")
        
        self.render('deploy/pack.html', proj_list = proj_list ,clecs_list = clecs_list)
    @tornado.web.authenticated     
    def post(self):
        
        type = self.get_argument('type', None)
        proj = self.get_argument('proj', None)
        version = self.get_argument('version', None)
        clecs = self.get_argument('clecs', None)
        svn = self.get_argument('svn', None)
        svndir = self.get_argument('svndir', None)
            
        svn_ver = '' if version == '' else '-v %s' % (version)
        svndir_val = '' if svndir == '' else '-p %s' % (svndir)
        
        if proj == 'yxgj' :
            self.TIMEOUT_COMMAND('cd /home/deploy/mbfabu && nohup /bin/bash deploy_mb.sh -c prod -t %s -a %s -s %s %s %s  >> dp.out 2>&1  &' % (type ,clecs, svn , svndir_val, svn_ver),10)
        elif proj == 'qnzm':
            self.TIMEOUT_COMMAND('cd /home/deploy/fabu && nohup /bin/bash deploy.sh -c prod -t %s -a %s -s %s %s %s  >> dp.out 2>&1  &' % (type ,clecs, svn , svndir_val, svn_ver),10)
        #self.write("<script>alert('新增成功！');history.back(-1)</script>")
        
class DeployHandler(BaseHandler):
    '''
        job_status = 1:success  2:faild  3:send  4:unknow
    '''
    @tornado.web.authenticated
    def get(self):
        
        proj_list = self.db.query("select * from ops_proj")
        clecs_list = self.db.query("select * from ops_clecs")
        
        self.render('deploy/deploy.html', proj_list = proj_list, clecs_list = clecs_list)
    @tornado.web.authenticated    
    def post(self):
        
        clecs = self.get_argument('clecs', None)
        proj = self.get_argument('proj', None)
        type = self.get_argument('type', None)
        version = self.get_argument('package', None)
        area = self.get_arguments('area', None)
        action = self.get_argument('action', None)
        
        if area and version:
            
            area_arr = []
            job_dic = {}
            
            #insert to job table job_id
            job_id = self.db.execute_lastrowid("insert ops_job(job_type,job_user,job_time) values(1,%s,UNIX_TIMESTAMP())", self.user_header)
            
            for i in area:
                if type == 'server':
                    
                    area_query = self.db.get("select area_id,server_wan_ip from ops_area as a left join ops_server as b on a.area_host=b.server_id  where id=%s", i)
                    
                elif type == 'db':
                    
                    area_query = self.db.get("select area_id,server_wan_ip from ops_area as a left join ops_server as b on a.area_db=b.server_id  where id=%s", i)
                    
                if job_dic.get(area_query['server_wan_ip']):
                        
                    job_dic[area_query['server_wan_ip']] = job_dic[area_query['server_wan_ip']] , area_query['area_id']
                else:
                        
                    job_dic[area_query['server_wan_ip']] = area_query['area_id']
            
            check_list = []
            
            #insert to joblist table
            for k,v in job_dic.items():
                
                if isinstance(v, tuple):
                    job_area = ','.join('%s' % area_tuple for area_tuple in v)
                else:
                    job_area = v
            
                #job_command = {"-p":proj, "-t":type, "-a":action, "-s":job_area, "-c":clecs, "-v":version, "-h":"127.0.0.1"}
                job_command = '-p:%s -t:%s -a:%s -s:%s -c:%s -v:%s -h:127.0.0.1' % (proj,  type, action, job_area, clecs, version)
                
                joblist_id = self.db.execute_lastrowid("insert ops_joblist(job_id,joblist_objective,joblist_command,joblist_type) values(%s, %s, %s, %s)" , job_id, k, job_command, 1)
                
                check_dic = {"jid":joblist_id, "ip":k, "command":job_command, "area":job_area}
                
                check_list.append(check_dic)
            
        else:
             
             self.write("<script>alert('某些未选择！');history.back(-1)</script>") 
             return None    
        
        self.render('deploy/deploy_job.html', proj = proj, clecs = clecs, type = type, action = action, version = version, check_list = check_list, job_type = 1, job_id = job_id) 
        
class GetPackageHandler(BaseHandler):
    
    '''
        for ajax use
        
    '''
    @tornado.web.authenticated
    def get(self):
        
        type = self.get_argument('type', None)
        clecs = self.get_argument('clecs', None)
        proj = self.get_argument('proj', None)
        
        package_list = self.get_update(type,clecs,proj)
        
        
        self.write(json.dumps(package_list))
        
        
class GetAreaHandler(BaseHandler):
    
    '''
        for ajax use
            
    '''
    @tornado.web.authenticated
    def get(self):
        
        clecs = self.get_argument('clecs', None)
        proj = self.get_argument('proj', None)
        
        area_list = self.db.query("select a.id,a.area_id,a.area_name,b.server_wan_ip as serverip,c.server_wan_ip as dbip from ops_area as a left join ops_server as b on a.area_host=b.server_id left join ops_server as c on a.area_db=c.server_id left join ops_proj as d on a.area_proj=d.proj_id where area_clecs=%s and d.proj_alias=%s order by a.id desc", clecs, proj)
        
        self.write(json.dumps(area_list))
        
        
class GetReadyHandler(BaseHandler):
    
    '''
        fox ajax use
        
    '''
    @tornado.web.authenticated
    def post(self):
        
        joblist_id = self.get_argument('jid', None)
        
        if joblist_id:
            
            code = self.db.get("select joblist_status from ops_joblist where id=%s",joblist_id)
            
            self.write(str(code['joblist_status']))
        
    
class MakeJobHandler(SocketHandler):
    
    @tornado.web.authenticated
    def post(self):
        
        job_id = self.get_argument('jobid', None)
        
        if job_id:
            
            joblist = self.db.query("select * from ops_joblist where job_id=%s",job_id)
            
            for i in joblist:
                
                ipaddr = i['joblist_objective']
                command = i['joblist_command']
                
                send = self.send_socket(type=1, id=i['id'], ipaddr=ipaddr, command=command)
                
#                 if send :
#                     self.db.execute("update ops_joblist set joblist_status=4,joblist_start_time=UNIX_TIMESTAMP() where id=%s", i['id'])
#                 else:
#                     self.db.execute("update ops_joblist set joblist_status=6,joblist_start_time=UNIX_TIMESTAMP() where id=%s", i['id'])
                    
                    
class ReportJobHandler(BaseHandler):
    
    def post(self):
        
        joblist_id = self.get_argument('jid', None)
        job_status = self.get_argument('status', None)
        job_log = self.get_argument('log', None)
        
        id_check = self.db.get("select id from ops_joblist where id=%s",joblist_id)
        
        if id_check: 
            
            try:
                self.db.execute("update ops_joblist set joblist_status=%s,joblist_log=%s,joblist_endtime=UNIX_TIMESTAMP() where id=%s",job_status, job_log, joblist_id)
                self.write('true')
            except:
                self.write('false')
                
            
class AreaListHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        if  self.get_argument("page", None):
            page = int(self.get_argument("page", None))
        else:
            page = 1
        
        pagenum = 20
        
        page_limit = self.get_page_limit(page, pagenum)  
        page_count = self.db.execute_rowcount("select * from ops_area")
        
        self.db.execute("update ops_area set area_state=Null,area_install=Null,area_version=Null")
        area_list = self.db.query("select a.id,proj_name,clecs_name,area_id,area_name,d.server_wan_ip as serverip from ops_area as a LEFT JOIN ops_clecs as b on a.area_clecs = b.clecs_id LEFT JOIN ops_proj as c on a.area_proj=c.proj_id LEFT JOIN ops_server as d on a.area_host=d.server_id order by id desc limit %s,%s", page_limit, pagenum)
        
        for i in area_list:
            AreaListSocket(i['id'], i['area_id'], i['serverip'])

        self.render('deploy/area.html', area_list = area_list, page = page, pagenum = pagenum, page_count = page_count)  
                
        
        
        
class AreaListSocket(SocketHandler):
    
    def __init__(self, id, area_id, ip):
        
        job_command = '-get:area -p:yxgj -t:server -s:%s' % (area_id)
        
        bc = self.send_socket(type=3, id=id, ipaddr=ip, command=job_command)
        
        
class ServerActionHandler(SocketHandler):
    
    @tornado.web.authenticated
    def post(self):
        
        area_id = self.get_argument('id', None)
        action = self.get_argument('action', None)
        
        server_info = self.db.get("select server_wan_ip as ip,proj_alias,area_id from ops_area as a left join ops_server as b on a.area_host=b.server_id left join ops_proj as c on a.area_proj=c.proj_id where a.id=%s", area_id)
        
        if server_info:
        
            job_id = self.db.execute_lastrowid("insert ops_job(job_type,job_user) values(1,%s)", self.user_header)
            
            job_command = '-p:%s -t:server -a:%s -s:%s -c:888 -v:0 -h:127.0.0.1' % (server_info['proj_alias'], action, server_info['area_id'])
            joblist_id = self.db.execute_lastrowid("insert ops_joblist(job_id,joblist_objective,joblist_command,joblist_type) values(%s, %s, %s, %s)" , job_id, server_info['ip'], job_command, 1)
            
            self.send_socket(type=1, id=joblist_id, ipaddr=server_info['ip'], command=job_command)
        
        
class JobViewHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        if  self.get_argument("page", None):
            page = int(self.get_argument("page", None))
        else:
            page = 1
        
        pagenum = 20
        
        page_limit = self.get_page_limit(page, pagenum)  
        page_count = self.db.execute_rowcount("select * from ops_job")
        
        job_list = self.db.query("select * from ops_job order by job_id desc limit %s,%s", page_limit, pagenum)
        
        self.render('deploy/job.html', job_list = job_list, page = page, pagenum = pagenum, page_count = page_count)  
        
        
class GetJobStatusHandler(BaseHandler):
    
    
    @tornado.web.authenticated
    def post(self): 
        job_id = self.get_argument('jid', None)
        joblist_info = self.db.query("select joblist_status from ops_joblist where job_id=%s", job_id)
        
        joblist_arr = []
        
        for i in joblist_info:
            if i['joblist_status'] == 2:
                self.write("2")
                return 
            
            joblist_arr.append(i['joblist_status'])
        
        if len(joblist_arr) != 0:
            
            self.write(str(max(joblist_arr))) 
        else:
            self.write("0")
            
    @tornado.web.authenticated        
    def get(self):
        job_id = self.get_argument('jid', None)
        joblist_info = self.db.query("select * from ops_joblist where job_id=%s", job_id)
           
        
        self.render('deploy/job_list.html', joblist_info = joblist_info, job_id = job_id ) 
        
        
        
            
            
            
            
        
        
        
        
        