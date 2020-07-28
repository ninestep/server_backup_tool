服务器资料备份工具

在`program/config.yaml`文件里配置，具体参考备注

目前支持的备份类型为文件和mysql数据库
备份的文件需要映射到docker中
备份的数据库要保证docker可以访问到

启动方法：`docker-compose up -d python`
> 如果设置了百度网盘备份，方法由两种
> 1. 运行`docker-compose run --rm python python lead.py`为百度网盘授权
> 2. 直接访问`https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=deSrTwIBCc4ysSqTMrkCQSpv&redirect_uri=oob&scope=basic,netdisk&display=tv&qrcode=1&force_login=1`, 并将授权码粘贴到`program\config.yaml`中，直接运行`docker-compose up -d python` 即可
> 因为授权码只在十分钟内有效，且每个授权码仅可使用1次，所以注意更新。

`mysql` 为测试使用的数据库

后期计划
- [x] 增加百度网盘备份支持
- [ ] 增加onedrive备份支持
- [ ] 增加sqlserver备份支持