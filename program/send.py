import smtplib, time, requests, os, hashlib, json
import log, traceback
from Tools import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import configparser
import lead
from requests.adapters import HTTPAdapter

cf = configparser.ConfigParser()
cf.read("/program/cache.ini", encoding="utf-8")  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

logTool = log.logs()
conf = Config()


class Mail:
    def __init__(self):
        mail_conf = conf.get('save')['mail']
        self.host = mail_conf['host']
        self.port = mail_conf['port']
        self.to = mail_conf['to']
        self.user = mail_conf['user']
        self.password = mail_conf['password']

    def save(self, path, name):

        dt = datetime.now()
        logTool.info('开始构建邮件')
        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = Header("备份服务器", 'utf-8')
        subject = "%s-%s备份数据" % (name, dt.strftime('%Y/%m/%d %H:%M:%S'))
        message['Subject'] = Header(subject, 'utf-8')

        # 邮件正文内容
        message.attach(MIMEText("%s-%s备份数据" % (name, dt.strftime('%Y/%m/%d %H:%M:%S')), 'plain', 'utf-8'))

        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(open(path, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename="%s"' % (path)
        message.attach(att1)

        logTool.info('邮件构建成功，开始发送')
        try:
            smtp_obj = smtplib.SMTP_SSL(self.host, self.port)
            smtp_obj.login(self.user, self.password)
            smtp_obj.sendmail(self.user, [self.to], message.as_string())
            logTool.info('邮件发送成功')
        except smtplib.SMTPException:
            logTool.info('邮件发送失败,错误信息%s' % traceback.format_exc())


class Baidu:
    def __init__(self):
        bd_conf = conf.get('save')['baidu']
        self.client_id = bd_conf['client_id']
        self.secret_key = bd_conf['secret_key']
        self.save_path = bd_conf['save_path']
        self._get_cache()
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=3))
        self.s.mount('https://', HTTPAdapter(max_retries=3))
        if (int(self.expires_in) + int(self.update) - 100) <= int(time.time()):
            self._refresh_token()
            self._get_cache()

    def _get_cache(self):
        self.cf = configparser.ConfigParser()
        self.cf.read("/program/cache.ini", encoding="utf-8")
        if 'baidu' not in self.cf:
            lead.baidu()
            self.cf = configparser.ConfigParser()
            self.cf.read("/program/cache.ini", encoding="utf-8")
        self.expires_in = self.cf.get('baidu', 'expires_in')
        self.refresh_token = self.cf.get('baidu', 'refresh_token')
        self.access_token = self.cf.get('baidu', 'access_token')
        self.session_secret = self.cf.get('baidu', 'session_secret')
        self.scope = self.cf.get('baidu', 'scope')
        self.update = self.cf.get('baidu', 'update')

    def _refresh_token(self):
        url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=refresh_token&refresh_token=%s &client_id=%s&client_secret=%s' % (
            self.refresh_token, self.client_id, self.secret_key)
        res = self.s.get(url)
        res = res.json()
        if 'error' in res:
            logTool.error('返回出错，错误代码：%s。错误信息：%s.具体请参阅%s' % (
                res['error'], res['error_description'], 'https://developer.baidu.com/newwiki/dev-wiki/fu-lu.html'))
            raise requests.HTTPError('返回出错，错误代码：%s。错误信息：%s.具体请参阅%s' % (
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
            print('百度网盘重新获取权限成功')

    def get_free_space(self):
        """
        获取空闲空间大小,单位B
        :return:
        """
        url = "https://pan.baidu.com/api/quota?access_token=%s&chckfree=1&checkexpire=1" % self.access_token
        res = self.s.get(url)
        res = res.json()
        if 'error' in res:
            logTool.error('返回出错，错误代码：%s。错误信息：%s.具体请参阅%s' % (
                res['error'], res['error_description'], 'https://developer.baidu.com/newwiki/dev-wiki/fu-lu.html'))
            raise requests.HTTPError('返回出错，错误代码：%s。错误信息：%s.具体请参阅%s' % (
                res['error'], res['error_description'], 'https://developer.baidu.com/newwiki/dev-wiki/fu-lu.html'))
        else:
            return res['free']

    def save(self, path, name):
        [file_path, filename] = os.path.split(path)
        file_size = os.path.getsize(path)
        if file_size >= 4294967296:
            logTool.info('%s,大小大于4G，开始拆分' % name)
            try:
                file_list = self._file_chunkspilt(path, 4294967200)
            except Exception as e:
                print(e)
                raise e
            logTool.info('文件%s切分为%s份' % (path, len(file_list)))
            for i, val in enumerate(file_list):
                self.save(val['path'], os.path.join(name, os.path.basename(path)))
            return True
        else:
            bd_path = os.path.join(self.save_path, name, filename)
            logTool.info('开始备份%s,文件将存贮到%s' % (name, bd_path))
            if file_size <= 4194304:
                file_list = [{
                    'path': path,
                    'md5': self._get_md5(path)
                }]
            else:
                logTool.info('文件%s大小%sM大于4M，切分文件' % (path, file_size / 1048576))
                file_list = self._file_chunkspilt(path)
                logTool.info('文件%s切分为%s份' % (path, len(file_list)))
            data = {
                "path": bd_path,
                "size": file_size,
                "isdir": 0,
                "autoinit": 1,
                "rtype": 1,
                "block_list": json.dumps(["%s" % x["md5"] for x in file_list]),
                "content-md5": self._get_md5(path)
            }
            header = {
                'User-Agent': 'pan.baidu.com'
            }
            url = 'https://pan.baidu.com/rest/2.0/xpan/file?method=precreate&access_token=%s' % self.access_token
            data = "&".join("{}={}".format(*i) for i in data.items())

            logTool.info('文件%s预上传' % path)
            res = self.s.post(url=url, data=data, headers=header).json()
            if int(res['errno']) != 0:
                logTool.error('%s 上传错误，错误代码%s' % (name, res['errno']))
                raise requests.HTTPError('%s 上传错误，错误代码%s' % (name, res['errno']))
            else:
                if int(res['return_type']) == 2:
                    logTool.info('%s 已上传，存储路径为%s' % (name, res['info']['path']))
                else:
                    logTool.info('文件%s分块上传' % path)
                    upload_id = res['uploadid']
                    data = {
                        "method": "upload",
                        "type": "tmpfile",
                        "path": bd_path,
                        "uploadid": res['uploadid']
                    }
                    block_list = []
                    for i, val in enumerate(file_list):
                        data['partseq'] = i
                        url = 'https://d.pcs.baidu.com/rest/2.0/pcs/superfile2?access_token=%s&%s' % (
                            self.access_token, "&".join("{}={}".format(*i) for i in data.items()))
                        files = {'file': open(val['path'], 'rb')}
                        try:
                            upload_res = self.s.post(url, files=files, timeout=None).json()
                        except requests.exceptions as e:
                            logTool.error('%s第%d个分块文件%s上传失败，错误代码%s' % e)
                            raise e
                        if 'errno' in upload_res:
                            logTool.error('%s第%d个分块文件%s上传失败，错误代码%s' % (path, i, val['path'], upload_res['errno']))
                            raise requests.HTTPError(
                                '%s第%d个分块文件%s上传失败，错误代码%s' % (path, i, val['path'], upload_res['errno']))
                        else:
                            block_list.append(upload_res['md5'])
                            if path != val['path']:
                                os.remove(val['path'])
                    logTool.info('文件上传完成，开始创建文件')
                    url = 'https://pan.baidu.com/rest/2.0/xpan/file?method=create&access_token=%s' % self.access_token
                    data = {
                        "path": bd_path,
                        "size": file_size,
                        "isdir": 0,
                        "uploadid": upload_id,
                        "rtype": 3,
                        "block_list": json.dumps(block_list)
                    }
                    encode_data = "&".join("{}={}".format(*i) for i in data.items())
                    create_res = self.s.post(url, data=encode_data, headers=header).json()
                    if 'errno' not in create_res or int(create_res['errno']) == 0:
                        logTool.info('%s文件上传成功' % (path))
                    else:
                        logTool.error('%s文件上传上传失败，错误代码%s' % (path, create_res['errno']))
                        raise requests.HTTPError('%s文件上传上传失败，错误代码%s' % (path, create_res['errno']))

    def _file_chunkspilt(self, filepath, chunksize=4194304):
        '''
        文件按照数据块大小分割为多个子文件
        INPUT  -> 文件目录, 文件名, 每个数据块大小
        '''
        file_list = []
        if chunksize > 0:
            partnum = 0
            inputfile = open(filepath, 'rb')
            [path, filename] = os.path.split(filepath)
            while True:
                chunk = inputfile.read(2048)
                newfilename = os.path.join(path, (filename + '_%04d' % partnum))
                if not chunk:
                    md5 = self._get_md5(newfilename)
                    file_list.append({
                        'path': newfilename,
                        'md5': md5,
                    })
                    break
                with open(newfilename, 'ab+') as sub_file:
                    sub_file.write(chunk)
                if (os.path.getsize(newfilename) + 2048 > chunksize):
                    partnum += 1
                    md5 = self._get_md5(newfilename)
                    file_list.append({
                        'path': newfilename,
                        'md5': md5,
                    })

            inputfile.close()
            return file_list
        else:
            print('chunksize must bigger than 0!')
            return []

    @staticmethod
    def _get_md5(file):
        m = hashlib.md5()
        with open(file, 'rb') as f:
            for line in f:
                m.update(line)
        md5code = m.hexdigest()
        return md5code
