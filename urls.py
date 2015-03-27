#coding:utf-8

from handlers.index import *
from handlers.proj import *
from handlers.deploy import *
from handlers.monitor import *
from handlers.manager import *

urls = [
        (r'/', IndexHandler),
        (r'/proj/ViewClecsHandler', ViewClecsHandler),
        (r'/proj/AddClecsHandler', AddClecsHandler),
        (r'/proj/EditClecsHandler', EditClecsHandler),
        (r'/proj/DeleteClecsHandler', DeleteClecsHandler),
        (r'/proj/ViewProjHandler', ViewProjHandler),
        (r'/proj/AddProjHandler', AddProjHandler),
        (r'/proj/EditProjHandler', EditProjHandler),
        (r'/proj/DeleteProjHandler', DeleteProjHandler),
        (r'/proj/ViewAreaHandler', ViewAreaHandler),
        (r'/proj/AddAreaHandler', AddAreaHandler),
        (r'/proj/EditAreaHandler', EditAreaHandler),
        (r'/proj/DeleteAreaHandler', DeleteAreaHandler),
        (r'/proj/ViewServerHandler', ViewServerHandler),
        (r'/proj/AddServerHandler', AddServerHandler),
        (r'/proj/EditServerHandler', EditServerHandler),
        (r'/proj/DeleteServerHandler', DeleteServerHandler),
        (r'/deploy/PackHandler', PackHandler),
        (r'/deploy/DeployHandler', DeployHandler),
        (r'/deploy/GetPackageHandler', GetPackageHandler),
        (r'/deploy/GetAreaHandler', GetAreaHandler),
        (r'/deploy/GetJobStatusHandler', GetJobStatusHandler),
        (r'/deploy/MakeJobHandler', MakeJobHandler),
        (r'/deploy/ReportJobHandler', ReportJobHandler),
        (r'/monitor/GetServerStatusHandler', GetServerStatusHandler),
        (r'/monitor/ServerHandler', ServerHandler),
        (r'/monitor/GetAreaStatusHandler', GetAreaStatusHandler),
        (r'/deploy/AreaListHandler', AreaListHandler),
        (r'/deploy/ServerActionHandler', ServerActionHandler),
        (r'/deploy/JobViewHandler', JobViewHandler),
        (r'/deploy/GetReadyHandler', GetReadyHandler),
        (r'/manager/UserViewHandler', UserViewHandler),
        (r'/manager/UserAddHandler', UserAddHandler),
        (r'/manager/UserEditHandler', UserEditHandler),
        (r'/manager/UserDelHandler', UserDelHandler),
        (r'/login', LoginHandler),
        (r'/logout', LogoutHandler),
        (r".*", PageNotFoundHandler)

        
]