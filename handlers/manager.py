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

    Handlers: site Manager 
    author: 13620459@qq.com

'''

from model.base import *
import hashlib

class UserViewHandler(BaseHandler):
    
    def get(self):
        
        user_list = self.db.query("select * from ops_user")
        
        self.render('manager/user_list.html',user_list = user_list)
        


class UserAddHandler(BaseHandler):
    
    def get(self):
        
        self.render('manager/user_add.html')
    
    def post(self):
        
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        
        if username and password:
            
            password_md5 = hashlib.md5(password.strip()).hexdigest()
            self.db.execute("insert into ops_user (username,password) values(%s,%s)", username , password_md5)
            self.write("<script>alert('新增成功！');history.back(-1)</script>") 
        

class UserEditHandler(BaseHandler):
    
    def get(self):
        userid = self.get_argument("id", None)
        
        if userid:
            user_info = self.db.get("select * from ops_user where userid=%s", userid)
            
            self.render('manager/user_edit.html', user_info = user_info)
            
    def post(self):
        
        userid = self.get_argument("userid", None)
        password = self.get_argument("password", None)
        
        if userid and password:
            password_md5 = hashlib.md5(password.strip()).hexdigest()
            self.db.execute("update ops_user set password=%s where userid=%s", password_md5, userid)
            self.write("<script>alert('修改成功！');history.back(-1)</script>")
            
class UserDelHandler(BaseHandler):
    
    def get(self):
        userid = self.get_argument("id", None)
        
        if userid:
            self.db.execute("delete from ops_user where userid=%s", userid)
            self.write("<script>history.back(-1)</script>")
        
