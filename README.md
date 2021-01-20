# BunKum
![project_license](https://badgen.net/badge/License/GPL-3.0/green)
![python-depend](https://badgen.net/badge/Python/3.6.8+/blue)
![flask-depend](https://badgen.net/badge/Flask/1.1.1+/yellow)
![bootstrap-depend](https://badgen.net/badge/Bootstrap/3.3.7/red)
![mysql-depend](https://badgen.net/badge/MySQL/5.7/orange)
![redis-depend](https://badgen.net/badge/Redis/4.0.9+/cyan)
![nginx-depend](https://badgen.net/badge/Nginx/1.14.0+/purple)

一个使用 `Python` 且基于 `Flask` Web 框架开发的 `MVC` 架构的个人博客系统。
***
## 功能介绍
- 用户系统
    - 用户注册，登录，登出
    - 用户权限及权限验证
    - 邮件地址验证
    - 基于邮件验证的密码重置、密码更改、邮箱地址更改
    - 用户资料页展示
      ![profile_pic](/screenshot/profile.gif)
    - 用户之间站内信
      ![message_pic](/screenshot/message.gif)
    - 用户头像的上传及修改
      ![avatar_pic](/screenshot/avatar_upload.gif)
- 博客系统
    - 发表博客
    - 文章分类及分类条目创建
    - 博客文章内容展示
    - 内容展示页内评论区
      ![new_blog_pic](/screenshot/new_blog.gif)
    - 文章及评论区 `Markdown` 语法支持
    - 文章及评论区代码高亮支持
      ![new_comment_pic](/screenshot/new_comment.gif)
    - 评论区 @ 其他用户及消息提醒
      ![comment_at_pic](/screenshot/comment_at.gif)
- 后台管理系统
    - 博客文章管理，包括文章编辑、删除、按分类显示，文章下评论显示
    - 文章分类管理，包括条目编辑、删除，显示分类下文章
    - 用户管理，包括用户信息编辑、删除，未认证用户显示，指定用户显示评论
    - 评论管理，包括评论编辑、删除，指定作者显示评论，指定文章评论显示，被屏蔽评论显示
    - 站内信管理，包括消息编辑、删除，显示指定发送者消息，显示指定接收者消息，单边删除显示
      ![management_pic](/screenshot/management.gif)
***
## 使用方法
### Ubuntu
*推荐版本：`Ubuntu 18.04 LTS`*  

在 `Ubuntu/Linux` 平台下，本项目使用 `Gunicorn` 配合 `Gevent` 网络库作为 Web 服务器，并使用 `Supervisor` 自动管理 `Gunicorn` 和 `Celery` 进程。同时使用 `Nginx` 作为反向代理服务器。  

**注意：** 在 `Ubuntu 20.04 LTS` 及以上版本的 `Ubuntu` 仓库中默认不再包含 `MySQL 5.7` 版本，需要自行手动安装。  
1. 初始化：  
    克隆仓库代码：  
    ```shell
    sudo git clone https://github.com/sentanl869/BunKum.git /var/www/BunKum
    ```
    进入项目目录：
    ```shell
    cd /var/www/BunKum
    ```
    创建环境变量文件：  
    ```shell
    sudo cp .env.example .env
    ```
    配置环境变量：
    ```dotenv
    MYSQL_PASSWORD=example #MySQL密码 注意：不要移动此项顺序，否则部署脚本会失效
    SECRET_KEY=example #Flask密钥
    ADMIN_ACCOUNT=example@example.com #设置博客管理员账户
    ADMIN_PASSWORD=example #设置博客管理员密码
    ADMIN_USERNAME=example #设置博客管理员用户名
    MAIL_SERVER=smtp.example.com #系统邮件发送地址
    MAIL_PORT=465 #系统邮件发送端口，默认使用SSL
    MAIL_USERNAME=example@example.com #系统邮件账户
    MAIL_PASSWORD=example #系统邮件密码
    MAIL_SENDER=no-reply<example@example.com> #系统邮件发件人 注意：发件人邮件地址与账户地址应保持一致
    DEFAULT_AVATAR_FILE_NAME=default_avatar.png #默认用户头像文件名称
    CELERY_BROKER_URL=redis://example:port/db_num #Celery消息中间件地址，默认使用Redis
    CELERY_RESULT_BACKEND=redis://example:port/db_num #Celery消息后台地址，默认使用Redis
    db_name=example #MySQL连接数据库名称
    db_user=example #MySQL连接用户名
    db_host=example #MySQL连接地址
    ```
2. 启动项目：  
    进入部署脚本目录：
    ```shell
    cd script
    ```
    执行一键部署脚本：
    ```shell
    sudo ./deploy.sh
    ```
    等待终端输出本机 IP 后，打开浏览器，在地址栏中输入网址 `localhost` 查看项目运行效果。
### Windows
在 `Windows` 平台下使用 `Vagrant` 搭配 `VirtualBox` 进行一键部署。
1. 安装 `Vagrant` 和 `VirtualBox`:  
    进入 [Vagrant](https://www.vagrantup.com/downloads.html) 官网和 [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 官网下载对应系统的安装包，进行安装即可。
2. 初始化：  
    克隆仓库代码：  
    ```shell
    git clone https://github.com/sentanl869/BunKum.git
    ```
    进入项目目录：
    ```shell
    cd BunKum
    ```
    创建环境变量文件：  
    ```shell
    cp .env.example .env
    ```
    配置环境变量：
    ```dotenv
    MYSQL_PASSWORD=example #MySQL密码 注意：不要移动此项顺序，否则部署脚本会失效
    SECRET_KEY=example #Flask密钥
    ADMIN_ACCOUNT=example@example.com #设置博客管理员账户
    ADMIN_PASSWORD=example #设置博客管理员密码
    ADMIN_USERNAME=example #设置博客管理员用户名
    MAIL_SERVER=smtp.example.com #系统邮件发送地址
    MAIL_PORT=465 #系统邮件发送端口，默认使用SSL
    MAIL_USERNAME=example@example.com #系统邮件账户
    MAIL_PASSWORD=example #系统邮件密码
    MAIL_SENDER=no-reply<example@example.com> #系统邮件发件人 注意：发件人邮件地址与账户地址应保持一致
    DEFAULT_AVATAR_FILE_NAME=default_avatar.png #默认用户头像文件名称
    CELERY_BROKER_URL=redis://example:port/db_num #Celery消息中间件地址，默认使用Redis
    CELERY_RESULT_BACKEND=redis://example:port/db_num #Celery消息后台地址，默认使用Redis
    db_name=example #MySQL连接数据库名称
    db_user=example #MySQL连接用户名
    db_host=example #MySQL连接地址
    ```
3. 启动项目：  
    在项目目录下执行：
    ```shell
    vagrant up
    ```
    等待终端输出虚拟机 IP 后，打开浏览器，在地址栏中输入网址 `localhost` 查看项目运行效果。  
    关于 `Vagrant` 的其他操作方法可以在官网 [查看](https://www.vagrantup.com/docs/cli) 。  