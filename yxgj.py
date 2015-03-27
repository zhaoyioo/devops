#! /usr/bin/env python
#coding=utf-8
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

import getopt, os, sys, shutil, pdb
import time
import urllib2, base64
import commands, re, string
import tarfile

#print os.getpid()

_GameName = 'yxgj'
_GameclientDir="/data/gameclient/"
_UpgradeDir="/data/Upgrade/"
_InitPort=8600
_ServerDir="/data/gameserver/%s/" % (_GameName)

_DownloadUrl="http://www.xxx.com/"

_RSYNC0="rsync -rlptvzP"
_RSYNC1="rsync -rlptvzP --delete"
_RSYNC2="--backup --backup-dir=$_BACKUP1/$(date +%F-%H%M%S)"
_RSYNC3="--exclude=*.pid --exclude=*.status"
_RSYNC4="--exclude=motif --exclude=upload --exclude=userfiles"

_FileName = 'U_cdkey.tar.gz'
_ProjLock="/tmp/game.lock"


def Server(_Action, _Sid, _Version, _Host, _Cid):
    
    if _Action in ['install', 'update']:
    
        _TarFile = "%s_server_%d_%d.tar.gz" % (_GameName, _Version, _Cid)
        _DownCheck = DownLoad_File(_UpgradeDir,_TarFile)
        
        if _DownCheck != True:
            return _DownCheck
        

    for _Sid_val in _Sid:
        
        _Sid_val = int(_Sid_val)
        _ServerPort = _InitPort + _Sid_val
        _GameDir = "%sS%d" % (_ServerDir,_Sid_val)
    
        if _Action == 'install':
        
            if os.path.exists(_GameDir):
                return "Error the ServerDir S%d aleady install" % (_Sid_val)
            
            ## mkdir gameserver dir
            try:    
                os.makedirs(_GameDir) 
            except OSError:
                return "mkdir %s access denied" %  (_GameDir)
            
            
            ## unzip & install gameserver file    
            _ZipCheck = Tar_File('unzip', _UpgradeDir + _TarFile, _GameDir)
            
            if _ZipCheck != True:
                return _ZipCheck
            
            ##create password for db
            _GameName_md5 = md5(_GameName)
            _DbPassword = md5("%s%dxxxxx####wokao####%s" % (_GameName_md5,_Sid_val,_Sid_val))
            
            _DbUserName = "%s_s%d" % (_GameName,_Sid_val)
            
            #初始化gameserver 配置文件
            _Config_xml = '''<?xml version="1.0" encoding="UTF-8"?>
            <root>
                <ID>%d</ID>
                <ServerPort>%d</ServerPort>
                <DatabaseUserName>%s</DatabaseUserName>
                <DatabasePassword>%s</DatabasePassword>
                <DatabaseIP>%s</DatabaseIP>
                <DatabasePort>3306</DatabasePort>
                <DatabaseName>%s</DatabaseName>
                <Log>33</Log>
                <FDB_UNIT>10240</FDB_UNIT>
                <PlatformId>%d</PlatformId>
            </root>''' % (_Sid_val, _ServerPort, _DbUserName, _DbPassword, _Host, _DbUserName, _Cid)
            
            f = file(_GameDir + "/config.xml", 'w') # open for 'w'riting
            f.write(_Config_xml) # write text to file
            f.close() # close the file
            
        elif _Action == 'update':
        
            if os.path.exists(_GameDir) == False:
                return "Error the ServerDir S%d not install" % (_Sid_val)
            
            ##check server status , stop it
            _ServerExec_a, _ServerExec_b = commands.getstatusoutput('cd %s && /bin/bash start.sh status' % (_GameDir))
            
            if _ServerExec_a == 0:
                #stop server first
                _ServerSh_a, _ServerSh_b = commands.getstatusoutput('cd %s && /bin/bash start.sh stop' % (_GameDir))
                if _ServerSh_a != 0:
                    return _ServerSh_b
            
            _ZipCheck = Tar_File('unzip', _UpgradeDir + _TarFile, _GameDir)
            
            if _ZipCheck != True:
                return _ZipCheck
        
        elif _Action == 'cache':
            
            ##check server status , gamedir 
            
            if os.path.exists(_GameDir) == False:
                return "Error the ServerDir S%d not install" % (_Sid_val)
            
            _PidFile = _GameDir + "/PIDDIR/Server.pid"
            if Check_Pid(_PidFile) == True:
                return "Error the Server S%d is running, stop it first" % (_Sid_val)
            
            try:    
                shutil.rmtree(_GameDir + '/fdb')
                shutil.rmtree(_GameDir + '/online')
            except OSError as e:
                return e
        
        elif _Action in ['start', 'stop', 'status']:
            
            if os.path.exists(_GameDir) == False:
                return "Error the ServerDir S%d not install" % (_Sid_val)
            
            _ServerExec_a, _ServerExec_b = commands.getstatusoutput('cd %s && /bin/bash start.sh %s' % (_GameDir, _Action))
            
            if _ServerExec_a != 0:
                return _ServerExec_b
            
        
    return True

        


def Db(_Action, _Sid, _Version, _Cid):
    
    ## check mysql system login
    _Login_a, _Login_b = commands.getstatusoutput('mysql -e "show databases" > /dev/null 2>&1')
    if _Login_a != 0:
        return "Error, can not login mysql"    
    
    ##creatre db & backup dir
    if os.path.exists(_UpgradeDir + "db") == False:
        os.makedirs(_UpgradeDir + "db") 
    if os.path.exists(_UpgradeDir + "backup") == False:
        os.makedirs(_UpgradeDir + "backup")
     
    _Table_TempDirNew = _UpgradeDir + "db/.table_new"
    _Table_TempDirOld = _UpgradeDir + "db/.table_old"

    if os.path.exists(_Table_TempDirNew) == False:
        os.makedirs(_Table_TempDirNew) 
    if os.path.exists(_Table_TempDirOld) == False:
        os.makedirs(_Table_TempDirOld)
        
    removeFileInFirstDir(_Table_TempDirNew)
    removeFileInFirstDir(_Table_TempDirOld)
    
    _TarFile = "%s_db_%d_%d.tar.gz" % (_GameName, _Version, _Cid)
    _DownCheck = DownLoad_File(_UpgradeDir,_TarFile)
        
    _DBfile1 = 'Game_init.sql'
    _DBfile2 = 'Game_sys.sql'    
    
    if _DownCheck != True:
        return _DownCheck
        
    _DbFileDir = _UpgradeDir + "db"
    _ModifyTable = _DbFileDir + "/mtable.sql"
    
    ## unzip & install gameserver file    
    _ZipCheck = Tar_File('unzip', _UpgradeDir + _TarFile, _DbFileDir)
            
    if _ZipCheck != True:
        return _ZipCheck
        
    for _Sid_val in _Sid:
            
        _Sid_val = int(_Sid_val)
        _DbName = "%s_s%d" % (_GameName,_Sid_val)
        
        ## get db list
        _DBList_a,_DBList_b = commands.getstatusoutput('mysql -e "show databases" | sed "1d"')
        _Db_search = re.search( r'%s' % (_DbName), _DBList_b, re.M)
        
        if _Action == 'install':
            
            if _Db_search:
                return "Error , database %s was aleady install" % (_DbName)
                
            ##create password for db
            _GameName_md5 = md5(_GameName)
            _DbPassword = md5("%s%dzhaoyi###yunji###%s" % (_GameName_md5,_Sid_val,_Sid_val))
            
            _DbCommand = "create database if not exists %s default character set utf8;grant all privileges on %s.* to '%s'@'%%' identified by '%s';flush privileges;" % (_DbName, _DbName, _DbName, _DbPassword)
            
            _DbExec_a, _DbExec_b = commands.getstatusoutput('mysql -e "%s"' % (_DbCommand))
            
            if _DbExec_a != 0:
                return _DbExec_b
            
            ##load sql file
            _DbInit_a, _DbInit_b = commands.getstatusoutput("mysql %s < %s/%s" % (_DbName, _DbFileDir, _DBfile1))
            _DbSYS_a, _DbSYS_b = commands.getstatusoutput("mysql %s < %s/%s" % (_DbName, _DbFileDir, _DBfile2))
        
            if _DbInit_a != 0 or _DbSYS_a != 0:
                return _DbInit_b, _DbSYS_b
                
                
        if _Action == 'update':
            
            if not _Db_search:
                return "Error , database %s was not install" % (_DbName)
            
            ## backup db
            _Backup_a, _Backup_b = commands.getstatusoutput('mysqldump %s --default-character-set=utf8 > %s/backup/backup_%s.sql' % (_DbName, _UpgradeDir, _DbName))
            
            if _Backup_a != 0:
                return _Backup_b
            
            _DbCommand = "drop database IF EXISTS %s_update;create database IF NOT EXISTS %s_update;" % (_DbName, _DbName)
            
            _DbExec_a, _DbExec_b = commands.getstatusoutput('mysql -e "%s"' % (_DbCommand))
            
            if _DbExec_a != 0:
                return _DbExec_b
                
            _DbUpdate_a, _DbUpdate_b = commands.getstatusoutput("mysql %s_update < %s/%s" % (_DbName, _DbFileDir, _DBfile1))
            
            if _DbUpdate_a != 0:
                return _DbUpdate_b
                
            _NewTableList = commands.getoutput("mysql -Ne 'use %s_update;show tables;' | sed '1d' | egrep -v '^A_*|^S_*|^T_*'" % (_DbName)).split('\n')
            _OldTableList = commands.getoutput("mysql -Ne 'use %s;show tables;' | sed '1d' | egrep -v '^A_*|^S_*|^T_*'" % (_DbName)).split('\n')
            
            if _NewTableList == '' or _OldTableList == '':
                return "Error , _NewTableList or _OldTableList is null, error"
            
            ## one , table update 
            CheckTable = Check_Table(_NewTableList, _OldTableList, _DbName, _ModifyTable)
            if CheckTable != True:
                return CheckTable
            
            CreateNew = Create_TableFile(_NewTableList, _DbName + "_update", _Table_TempDirNew)      
            CreateOld = Create_TableFile(_OldTableList, _DbName , _Table_TempDirOld)
            if CreateNew != True or CreateOld != True:
                return CreateNew,CreateOld
                
            for _N in _NewTableList:
                _NewMd5 = commands.getoutput("md5sum %s/%s_table | awk '{print $1}'" % (_Table_TempDirNew, _N))
                _OldMd5 = commands.getoutput("md5sum %s/%s_table | awk '{print $1}'" % (_Table_TempDirOld, _N))
                
                if _NewMd5 != _OldMd5:
                    _ChangeTable_a,_ChangeTable_b = commands.getstatusoutput("mysql -e 'use %s;rename table %s to %s_old'" % (_DbName, _N, _N))
                    if _ChangeTable_a != 0:
                        return _ChangeTable_b
                    
                    _MkTable_a,_MkTable_b = commands.getstatusoutput("mysql %s < %s/%s_table" % (_DbName, _Table_TempDirNew, _N))
                    if _MkTable_a != 0:
                        return _MkTable_b
                    
                    _OldTable_field = []          
                    for _OF in open("%s/%s_field" % (_Table_TempDirOld, _N)): 
                        _OldTable_field.append(_OF.strip('\n'))
                      
                    _NewTable_field = []
                    for _NF in open("%s/%s_field" % (_Table_TempDirNew, _N)):
                        if _NF.strip('\n') in _OldTable_field:
                            _NewTable_field.append('`' + _NF.strip('\n') + '`')
                    
                    _Ins_field = ','.join(_NewTable_field)
                    
                    _InsTable_a,_InsTable_b = commands.getstatusoutput("mysql -e 'use %s;INSERT INTO %s (%s) select %s FROM %s_old'" % (_DbName, _N, _Ins_field, _Ins_field, _N))
                    if _InsTable_a != 0:
                        return _InsTable_b
                    
                    _DropTable = commands.getoutput("mysql -e 'use %s;drop table %s_old;'" % (_DbName, _N))
                          
            ##load syssql file
            _DbSys_a, _DbSys_b = commands.getstatusoutput("mysql %s < %s/%s" % (_DbName, _DbFileDir, _DBfile2))
            if _DbSys_a != 0:
                return _DbSys_b
        
    return True
                
                
                

def Check_Table(_NewTableList, _OldTableList, _DbName, _ModifyTable):
    ### check newtable ,do add 
    for _N in _NewTableList:
        if _N not in _OldTableList:
            _DbDump_a, _DbDump_b = commands.getstatusoutput("mysqldump -d %s_update %s > %s" % (_DbName, _N, _ModifyTable))
            if _DbDump_a != 0:
                return _DbDump_b
                    
            _DbUpdate_a, _DbUpdate_b = commands.getstatusoutput("mysql %s < %s" % (_DbName, _ModifyTable))
            if _DbUpdate_a != 0:
                return _DbUpdate_b
                
    ### check oldtable ,do del
    for _Old in _OldTableList:
        if _Old not in _NewTableList:
            _DbDel_a, _DbDel_b = commands.getstatusoutput("mysql -e 'use %s ;DROP table %s;'" % (_DbName, _Old))
            if _DbDel_a != 0:
                return _DbDel_b
                
    return True            
         
def Create_TableFile(_TableList, _DbName, _Table_Dir):
    for _N in _TableList:
        _DbDump_a, _DbDump_b = commands.getstatusoutput("mysqldump -d --compact %s %s > %s/%s_table" % (_DbName, _N, _Table_Dir, _N))
        if _DbDump_a != 0:
            return _DbDump_b
        
        _DbExec_a, _DbExec_b = commands.getstatusoutput("mysql -Ne 'use %s;SHOW FIELDS FROM %s;' | awk '{print $1}' > %s/%s_field" % (_DbName, _N, _Table_Dir, _N))
        if _DbExec_a != 0:
            return _DbExec_b
    
    return True
            
            
def Useage():
    print '''
    -p Proj    Proj name       | yxgj & qnzm"
    -t Type    Type            | server & db & clent
    -a Action  Action          | install & update
    -s Sid     Server sid      | 1,2,3,4
    -c Cid     Clecs id        | 1 & 2 & 3
    -v Version svn version     | 8664
    -h Host    server db host  | 127.0.0.1
    --test     test mode       | 
    --delcache delete fdb      | 
    --help                     |
    '''

def Report(_Rstatus,_Rmessage):
    print _Rstatus,_Rmessage

    
    
def Check_Pid(_PidFile):
        
    try:
        _pf = file(_PidFile)
    except IOError as e:
        return False
    else:
        _pid = int(_pf.read())
        _pf.close()
        a,b = commands.getstatusoutput("ps -p %d" % (_pid))
        if a == 0:
            return True
        else:
            return False
        

def Tar_File(_TarAct,_TarFile,_TarPath):
    
    if _TarAct == 'unzip':
        try:
            tar = tarfile.open(_TarFile)
        except IOError as e:
            return e
        except:
            return sys.exc_info()[0]
        else:
            tar.extractall(path=_TarPath)
            tar.close()
        return True
    elif _TarAct == 'zip':
        try:
            tar = tarfile.open(_TarFile,'w:gz')

        except IOError as e:
            return e
        except: 
            return sys.exc_info()[0]
        else:
            for root, dir, files in os.walk(_TarPath):
                for file in files:
                    fullpath = os.path.join(root,file)
                    tar.add(fullpath,arcname=file)
            tar.close()
        return True    
        
def DownLoad_File(_FilePath,_FileName):
    '''
        HTTP更新包下载服务器做了个简单的验证,此处是使用用户名密码下载
    '''
    request = urllib2.Request(_DownloadUrl + _FileName)
    base64string = base64.encodestring('%s:%s' % ('xxx', 'xxxxxxxxx')).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    try:
        result = urllib2.urlopen(request, timeout=5)
    except urllib2.HTTPError as e:
        return e
    except urllib2.URLError as e:
        return e
    except: 
        return sys.exc_info()[0]
    else:
        data = result.read()
        with open(_FilePath + _FileName, "wb") as code:
            code.write(data)
        return True

def md5(str):
    import hashlib
    m = hashlib.md5()   
    m.update(str)
    return m.hexdigest()        
 

def removeFileInFirstDir(targetDir): 
    for file in os.listdir(targetDir): 
        targetFile = os.path.join(targetDir,  file) 
        if os.path.isfile(targetFile): 
            os.remove(targetFile) 


def main():
    
    if len(sys.argv) == 1:
        Useage()
        sys.exit()
        
    try:  
        opts, args = getopt.getopt(sys.argv[1:], "p:t:a:s:c:v:h:i:", ["test", "help", "delcache"])
        for op, value in opts:
            if op == "-p":
                _Proj = value
            elif op == "-t":
                _Type = value
            elif op == "-a":
                _Action = value
            elif op == "-s":
                _Sid = value.split(',')       
            elif op == "-c":
                _Cid = int(value)
            elif op == "-v":
                _Version = int(value)
            elif op == "-h":
                _Host = value
            elif op == "-i":
                _Id = value
            elif op == "--test":
                _TestMode = 1
            elif op == "--help":
                Useage()
                sys.exit()        
    except getopt.GetoptError:  
        Useage()
        sys.exit()

    if _Type == 'server':
        
        _MainFun = Server(_Action, _Sid, _Version, _Host, _Cid)
        
        print _MainFun

    elif _Type == 'db':
        
        _MainFun = Db(_Action, _Sid, _Version, _Cid)
        
        print _MainFun

    elif _Type == 'res':
        pass


if __name__ == '__main__':
    main()


    
           
#print opts
#DownLoad_File(_FileName)
