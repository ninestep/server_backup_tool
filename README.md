服务器资料备份工具

在`program/config.yaml`文件里配置，具体参考备注

目前支持的备份类型为文件和mysql数据库
备份的文件需要映射到docker中
备份的数据库要保证docker可以访问到

# 启动方法：
## 1. docker-compose
`docker-compose up -d python`
`mysql` 为测试使用的数据库

## 2. docker
`docker run -v path/to/config.yaml:/program/config.yaml`

> 如果设置了百度网盘备份，方法由两种
> 1. 运行`docker-compose run --rm python python lead.py`为百度网盘授权
> 2. 直接访问`https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=deSrTwIBCc4ysSqTMrkCQSpv&redirect_uri=oob&scope=basic,netdisk&display=tv&qrcode=1&force_login=1`, 并将授权码粘贴到`program\config.yaml`中，直接运行`docker-compose up -d python` 即可
> 因为授权码只在十分钟内有效，且每个授权码仅可使用1次，所以注意更新。



# 后期计划
- [x] 增加百度网盘备份支持
- [ ] 增加onedrive备份支持
- [ ] 增加sqlserver备份支持

# 配置文件格式
~~~
# 默认配置
default:
  save_path : /program/back/ #压缩文件保存地址
# 备份选项
save:
  mail: #备份名字
    type: Mail #备份类型，目前支持Mail邮箱
    host: smtp.qq.com #SMTP 服务器主机
    port: 465 # SMTP 服务使用的端口号
    user: '****@qq.com' # 发送的邮箱账号
    password: '****' # 发送的邮箱密码
    to: '****@qq.com' #接收邮件的邮箱
  baidu:
    type: Baidu
    client_id: deSrTwIBCc4ysSqTMrkCQSpv
    secret_key: DHhcOkElVNb2qUXDM7Vvx3emWx65GbeB
    save_path: '/server/backup/'
    authorization_code: '' #授权码粘贴到这里

# 备份配置
back_up:
#  test: #备份名称，不可重复
#    type: file #备份类型，file文件，其他为数据库类型
#    path: /program/admin #备份路径
#    backup_type: increment # 备份类型，quantity全量备份，increment增量备份，数据库统一进行全量备份
#    save_name: mail #对应save里面配置的选项
#    cron: "*/59 * * * *" #cron格式时间戳
  mysql:
    type: mysql
    address: mysql #数据库地址
    database: default #指定数据库
    port: 3306 #数据库端口
    username: root #用户名
    password: root #密码
    save_name: baidu
    cron: "*/1 * * * *"
~~~