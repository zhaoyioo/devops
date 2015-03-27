# devops
python游戏发布平台 

1 采用B/S结构  web控制台（tornado ） 向各游戏服务器节点agent(python)  发送指令

2 通讯部分使用了非阻塞socket协议 并使用了tornado的iostream 异步封装 , 保证web控制台批量与agent通讯效率, 通讯做了简单的加密验证,部分使用字节流传输

3 主要实现的功能有 部署游戏区服服务端,数据库,更新,启停服,获取区服状态,agent运行状态等,只是个框架 还有很多细化的功能可以做

4 主要流程如图, 目前SVN代码编译成更新包部分还是采用之前的shell脚本,有时间也可以改成python的(不过没啥必要)

5 agent.py 是常驻运行在 游戏节点服务器上接收指令和分发操作的, yxgj.py是针对某款游戏进行操作的, 增加游戏只需要增加单个py脚本就可以

6 yxgj.py  实现了个比较麻烦的mysql更新,能够更新mysql表结构 

7 运行web控制台 python server.py 默认监听9999端口   agent监听8742

8 水平有限 开发较快 , 第一次使用tornado , 小学生级别 大神勿喷 同段位小学生交流邮箱 13620459@qq.com

