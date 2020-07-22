import smtplib
import log, traceback
from Tools import Config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

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
