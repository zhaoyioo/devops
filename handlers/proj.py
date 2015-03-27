#coding:utf-8

from httplib import HTTPResponse
from model.base import *


class ViewClecsHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        #print self.__class__.__name__
        clecs = self.db.query("select * from ops_clecs")
        self.render('proj/clecs_list.html', clecs = clecs)
                

class AddClecsHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        self.render('proj/clecs_add.html')
    
    @tornado.web.authenticated    
    def post(self):
        
        clecs_id = self.get_argument('clecs_id', None)
        clecs_name = self.get_argument('clecs_name', None)
        if not clecs_id or not clecs_name:
            self.write("<script>alert('输入不能为空！');history.back(-1)</script>")
            return None
        
        self.db.execute("insert into ops_clecs(clecs_id, clecs_name,add_time) values(%s,%s,UNIX_TIMESTAMP())", clecs_id, clecs_name)
        self.write("<script>alert('新增成功！');history.back(-1)</script>")
        
        
class EditClecsHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        clecs_id = self.get_argument("clecs_id", None)
        
        if clecs_id:
            clecs_val = self.db.get("SELECT * FROM ops_clecs WHERE clecs_id = %s", int(clecs_id))
            
        self.render('proj/clecs_edit.html', clecs_val = clecs_val)
    
    @tornado.web.authenticated 
    def post(self):
        
        clecs_id = self.get_argument("clecs_id", None)
        clecs_name = self.get_argument('clecs_name', None)
        
        if clecs_id:
            self.db.execute("update ops_clecs set clecs_name=%s where clecs_id=%s", clecs_name, int(clecs_id))
            self.write("<script>alert('修改成功！');history.back(-1)</script>")
            
            
class DeleteClecsHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        clecs_id = self.get_argument("clecs_id", None)
        
        if clecs_id:
            self.db.execute("delete from ops_clecs where clecs_id=%s", int(clecs_id))
            self.write("<script>location.href = document.referrer;</script>")
        
            
class ViewProjHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        proj_list = self.db.query("select * from ops_proj")
        self.render('proj/proj_list.html', proj_list = proj_list)
        
        
class AddProjHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        self.render('proj/proj_add.html')
    @tornado.web.authenticated   
    def post(self):

        proj_name = self.get_argument('proj_name', None)
        proj_alias = self.get_argument('proj_alias', None)
        proj_svn = self.get_argument('proj_svn', None)
        
        if not proj_name or not proj_alias:
            self.write("<script>alert('输入不能为空！');history.back(-1)</script>")
            return None
        
        self.db.execute("insert into ops_proj(proj_name, proj_alias, proj_svn) values(%s, %s, %s)", proj_name, proj_alias, proj_svn)
        self.write("<script>alert('新增成功！');history.back(-1)</script>")
          
        
class EditProjHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        proj_id = self.get_argument("proj_id", None)
        
        if proj_id:
            proj_val = self.db.get("SELECT * FROM ops_proj WHERE proj_id = %s", int(proj_id))
            
        self.render('proj/proj_edit.html', proj_val = proj_val)
    
    @tornado.web.authenticated   
    def post(self):
        
        proj_id = self.get_argument("proj_id", None)
        proj_name = self.get_argument('proj_name', None)
        proj_alias = self.get_argument('proj_alias', None)
        proj_svn = self.get_argument('proj_svn', None)
        
        if proj_id:
            self.db.execute("update ops_proj set proj_name=%s,proj_alias=%s,proj_svn=%s where proj_id=%s", proj_name, proj_alias, proj_svn, int(proj_id))
            self.write("<script>alert('修改成功！');history.back(-1)</script>")
            
            
class DeleteProjHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        proj_id = self.get_argument("proj_id", None)
        
        if proj_id:
            self.db.execute("delete from ops_proj where proj_id=%s", int(proj_id))
            self.write("<script>location.href = document.referrer;</script>")
            
            
class ViewAreaHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        if  self.get_argument("page", None):
            page = int(self.get_argument("page", None))
        else:
            page = 1
        
        pagenum = 20
        
        page_limit = self.get_page_limit(page, pagenum)
        
        page_count = self.db.execute_rowcount("select * from ops_area")
        
        area_list = self.db.query("select a.id,proj_name,clecs_name,area_id,area_name,d.server_wan_ip as serverip,e.server_wan_ip as dbip from ops_area as a LEFT JOIN ops_clecs as b on a.area_clecs = b.clecs_id LEFT JOIN ops_proj as c on a.area_proj=c.proj_id LEFT JOIN ops_server as d on a.area_host=d.server_id LEFT JOIN ops_server as e on a.area_db=e.server_id order by id desc limit %s,%s", page_limit, pagenum)

        self.render('proj/area_list.html', area_list = area_list, page = page, pagenum = pagenum, page_count = page_count)


class AddAreaHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        server_list = self.db.query("select * from ops_server")
        clecs_list = self.db.query("select * from ops_clecs")
        proj_list = self.db.query("select * from ops_proj")
        
        self.render('proj/area_add.html', server_list = server_list, clecs_list = clecs_list, proj_list = proj_list)
    
    @tornado.web.authenticated    
    def post(self):
        
        area_id = self.get_argument('area_id', None)
        area_name = self.get_argument('area_name', None)
        area_host = self.get_argument('area_host', None)
        area_db = self.get_argument('area_db', None)
        area_clecs = self.get_argument('area_clecs', None)
        area_proj = self.get_argument('area_proj', None)
        
        if not area_id or not area_name or not area_host :
            self.write("<script>alert('输入不能为空！');history.back(-1)</script>")
            return None
        
        self.db.execute("insert into ops_area(area_id, area_name, area_host, area_db, area_clecs, area_proj) values(%s, %s, %s, %s, %s, %s)", area_id, area_name, area_host, area_db, area_clecs, area_proj)
        self.write("<script>alert('新增成功！');history.back(-1)</script>")


class EditAreaHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        id = self.get_argument("id", None)
        
        server_list = self.db.query("select * from ops_server")
        clecs_list = self.db.query("select * from ops_clecs")
        proj_list = self.db.query("select * from ops_proj")
        
        if id:
            area_val = self.db.get("SELECT * FROM ops_area WHERE id = %s", int(id))
            
        self.render('proj/area_edit.html', server_list = server_list, clecs_list = clecs_list, proj_list = proj_list, area_val = area_val)
    
    @tornado.web.authenticated    
    def post(self):
        
        id = self.get_argument('id', None)
        area_id = self.get_argument('area_id', None)
        area_name = self.get_argument('area_name', None)
        area_host = self.get_argument('area_host', None)
        area_db = self.get_argument('area_db', None)
        area_clecs = self.get_argument('area_clecs', None)
        area_proj = self.get_argument('area_proj', None)
        
        if id:
            self.db.execute("update ops_area set area_id=%s,area_name=%s,area_host=%s,area_db=%s,area_clecs=%s,area_proj=%s where id=%s", area_id, area_name, area_host, area_db, area_clecs, area_proj,int(id))
            self.write("<script>alert('修改成功！');history.back(-1)</script>")
            
            
class DeleteAreaHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        id = self.get_argument("id", None)
        
        if id:
            self.db.execute("delete from ops_area where id=%s", int(id))
            self.write("<script>location.href = document.referrer;</script>")

class ViewServerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        if  self.get_argument("page", None):
            page = int(self.get_argument("page", None))
        else:
            page = 1
        
        pagenum = 20
        
        page_limit = self.get_page_limit(page, pagenum)  
        page_count = self.db.execute_rowcount("select * from ops_server")
        
        server_list = self.db.query("select * from ops_server left join ops_room on ops_server.server_room=ops_room.room_id limit %s,%s",page_limit, pagenum)
        self.render('proj/server_list.html', projname = __name__, server_list = server_list, page = page, pagenum = pagenum, page_count = page_count)
        
        
class AddServerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        room_list = self.db.query("select * from ops_room")
        self.render('proj/server_add.html', room_list = room_list)
    
    @tornado.web.authenticated   
    def post(self):

        server_wan_ip = self.get_argument('server_wan_ip', None)
        server_lan_ip = self.get_argument('server_lan_ip', None)
        server_room = self.get_argument('server_room', None)
        server_other = self.get_argument('server_other', None)
        
        if not server_wan_ip or not server_room:
            self.write("<script>alert('输入不能为空！');history.back(-1)</script>")
            return None
        
        self.db.execute("insert into ops_server(server_wan_ip, server_lan_ip, server_room, server_other) values(%s, %s, %s, %s)", server_wan_ip, server_lan_ip, server_room, server_other)
        self.write("<script>alert('新增成功！');history.back(-1)</script>")
     
           
class EditServerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        server_id = self.get_argument("server_id", None)
        room_list = self.db.query("select * from ops_room")
        
        if server_id:
            server_val = self.db.get("SELECT * FROM ops_server WHERE server_id = %s", int(server_id))
            
        self.render('proj/server_edit.html', server_val = server_val, room_list = room_list)
   
    @tornado.web.authenticated   
    def post(self):
        
        server_id = self.get_argument('server_id', None)
        server_wan_ip = self.get_argument('server_wan_ip', None)
        server_lan_ip = self.get_argument('server_lan_ip', None)
        server_room = self.get_argument('server_room', None)
        server_other = self.get_argument('server_other', None)
        
        if server_id:
            self.db.execute("update ops_server set server_wan_ip=%s,server_lan_ip=%s,server_room=%s,server_other=%s where server_id=%s", server_wan_ip, server_lan_ip, server_room, server_other, int(server_id))
            self.write("<script>alert('修改成功！');history.back(-1)</script>")
            
            
class DeleteServerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        
        server_id = self.get_argument('server_id', None)
        
        if server_id:
            self.db.execute("delete from ops_server where server_id=%s", int(server_id))
            self.write("<script>location.href = document.referrer;</script>")



            
        
        

            
            