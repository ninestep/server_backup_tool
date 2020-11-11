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
        if self.database=='':
            try:
                # mysqldump -uroot -p123456 -A > /data/mysqlDump/mydb.sql
                cmd = "mysqldump -h%s -P %s -u%s -p%s --all-databases | gzip > %s" % (
                    self.address, self.port, self.username, self.password,  self.save_path
                )
                print(cmd)
                os.system(cmd)
            except Exception as e:
                logTool.error(e)
                raise e
        elif ',' in self.database:
            databases = self.database.split(',')
            for i, val in enumerate(databases):
                if val not in dbs:
                    del databases[i]
            if len(databases)<=0:
                logTool.error('未找到数据库%s' % self.database)
                raise KeyError('未找到数据库%s' % self.database)
            databases = ' '.join(databases)
            try:
                # mysqldump -uroot -p123456 --databases db1 db2 > /data/mysqlDump/mydb.sql
                cmd = "mysqldump -h%s -P %s -u%s -p%s --databases %s | gzip > %s" % (
                    self.address, self.port, self.username, self.password,databases , self.save_path
                )

                print(cmd)
                os.system(cmd)
            except Exception as e:
                logTool.error(e)
                raise e
        else:
            if self.database not in dbs:
                logTool.error('未找到数据库%s' % self.database)
                raise KeyError('未找到数据库%s' % self.database)
            try:
                cmd = "mysqldump -h%s -P %s -u%s -p%s %s | gzip > %s" % (
                    self.address, self.port, self.username, self.password, self.database, self.save_path
                )

                print(cmd)
                os.system(cmd)
            except Exception as e:
                logTool.error(e)
                raise e
