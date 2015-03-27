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

from model.base import *
import hashlib

class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('index/index.html')
        


class LoginHandler(BaseHandler):
    def get(self):
        
        self.render('common/login.html',msg = '') 
        
    def post(self):
        
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        
        password_md5 = hashlib.md5(password.strip()).hexdigest()
        
        check = self.db.get("select userid,username from ops_user where username=%s and password=%s", username, password_md5)
        
        if check:
            self.set_secure_cookie("user", username)
            self.redirect("/")
        else:
            self.render('common/login.html',msg = '<div class="alert alert-error"><strong>Error!</strong> 用户名或密码不正确.</div>') 
        
        
class LogoutHandler(BaseHandler):
    
    def get(self):
        
        self.clear_cookie('user')
        self.redirect("/")
        
        
class PageNotFoundHandler(BaseHandler):
    
    def get(self):
        raise tornado.web.HTTPError(404)
        