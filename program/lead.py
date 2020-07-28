from Tools import Config
import requests, time
import configparser

cf = configparser.ConfigParser()
cf.read("cache.ini", encoding="utf-8")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块
conf = Config()
save_conf = conf.get('save')


def baidu():
    # https://openapi.baidu.com/oauth/2.0/device/code?client_id=YOUR_CLIENT_ID&response_type=device_code& scope=basic,netdisk
    authorization_code = save_conf['baidu']['authorization_code']
    if len(authorization_code) <= 5:
        url = 'https://openapi.baidu.com/oauth/2.0/authorize?response_type=code&client_id=%s&redirect_uri=oob&scope=basic,netdisk&display=tv&qrcode=1&force_login=1' % (
            save_conf['baidu']['client_id'])
        code = input('请在浏览器中访问此地址，并将授权码回填\n%s\n请输入授权码:' % url)
    else:
        code = authorization_code
    url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=authorization_code&code=%s&client_id=%s&client_secret=%s&redirect_uri=oob' % (
        code, save_conf['baidu']['client_id'], save_conf['baidu']['secret_key'],)
    res = requests.get(url)
    res = res.json()
    if 'error' in res:
        print('返回出错，错误代码：%s。错误信息：%s.具体请参阅%s' % (
            res['error'], res['error_description'], 'https://developer.baidu.com/newwiki/dev-wiki/fu-lu.html'))
    else:
        if not cf.has_section('baidu'):
            cf.add_section('baidu')
        cf.set("baidu", "expires_in", str(res['expires_in']))
        cf.set("baidu", "refresh_token", res['refresh_token'])
        cf.set("baidu", "access_token", res['access_token'])
        cf.set("baidu", "session_secret", res['session_secret'])
        cf.set("baidu", "session_key", res['session_key'])
        cf.set("baidu", "scope", res['scope'])
        cf.set("baidu", "update", str(int(time.time())))
        with open('cache.ini', 'w') as fp:
            cf.write(fp)
        print('百度网盘登陆引导成功')


if __name__ == '__main__':
    baidu()
    # type_list = {
    #     '1': baidu,
    # }
    # choose = input('请选择引导的类型\r\n'
    #                '1.百度')
    # func = type_list[choose]
    # func()
