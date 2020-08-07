import os, pymysql
from log import logs

logTool = logs()


class mysql:
    def __init__(self, address, port, database, username, password, save_path):
        self.save_path = save_path
        self.address = address
        self.port = port
        self.database = database
        self.username = username
        self.password = password

    def _GetDatabaseNames(self):
        conn = pymysql.connect(self.address, self.username, self.password, use_unicode=True, charset="utf8")
        cur = conn.cursor()
        cur.execute('show databases;')
        dbs = cur.fetchall()
        data_list = [tuple[0] for tuple in dbs]
        cur.close()
        conn.close()
        return data_list

    def backUp(self):
        dbs = self._GetDatabaseNames()
        if self.database not in dbs:
            logTool.error('未找到数据库%s' % self.database)
            raise KeyError('未找到数据库%s' % self.database)
        try:
            cmd = "mysqldump -h%s -P %s -u%s -p%s %s | gzip > %s" % (
                self.address, self.port, self.username, self.password, self.database, self.save_path
            )
            os.system(cmd)
        except Exception as e:
            logTool.error(e)
            raise e
