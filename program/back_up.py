import tarfile, os
from datetime import datetime
from log import logs
from drive import *


class FullBack:
    def __init__(self, save_path):
        """
        针对指定数据进行完整备份
        :param save_path:压缩后的保存位置
        file:{path:'path_to_file_or_dir'}
        data:{
            type:'mysql_or_sqlserver',
            address:'link_to_database',
            port:port,
            database:database_name,
            user:database_user,
            password:database+password
        }
        """
        self.save_path = save_path
        self.tarfileTool = TarTool()
        self.logTool = logs()

    def BackUp(self, name, _type, args):
        """
        根据不同的参数触发不同的备份函数
        :param name: 备份名
        :param _type: 备份类型，file文件或文件夹，data数据库
        :param args:根据不太的类型，备份参数
        :return:压缩后的保存路径
        """
        if not os.path.isdir(os.path.join(self.save_path, name)):
            os.makedirs(os.path.join(self.save_path, name))
        if _type == 'file':
            self.logTool.info('检查到备份类型为文件，开始压缩')
            save_path = self._BackFile(name, args['path'])
            self.logTool.info('文件压缩成功,存储路径为%s' % save_path)
        else:
            self.logTool.info('检查到备份类型为数据库，开始压缩')
            save_path = self._BackDataBase(name, args['type'], args['address'], args['port'], args['database'],
                               args['username'], args['password'])
            self.logTool.info('数据库备份成功,备份路径为%s' % save_path)
        return save_path

    def _BackFile(self, name, path):
        """
        完整备份文件或文件夹
        :param name: 备份名字
        :param path: 备份路径
        :return:
        """
        dt = datetime.now()
        save_name = '%s/%s.tar.gz' % (name, dt.strftime('%Y%m%d%H%M%S%f'))
        save_path = os.path.join(self.save_path, save_name)
        self.tarfileTool.compress(path, save_path)
        return save_path

    def _BackDataBase(self, name, _type, address, port, database, username, password):
        """
        完整备份数据库
        :param name: 备份名字
        :param _type: 数据库类型，mysql或者sqlserver或者其他
        :param address: 数据库地址
        :param port: 端口
        :param database:备份的数据库
        :param username: 用户名
        :param password: 密码
        :return:
        """
        dt = datetime.now()
        save_name = '%s/%s.sql.gz' % (name, dt.strftime('%Y%m%d%H%M%S%f'))
        save_path = os.path.join(self.save_path, save_name)
        if _type == 'mysql':
            drive = mysql(address, port, database, username, password, save_path)
            drive.backUp()
        return save_path


class TarTool:
    def __init__(self, buf_size=1024 * 8):
        self.bufSize = buf_size
        self.fin = None
        self.fout = None
        self.logTool = logs()

    def compress(self, src, dst):
        self.logTool.info('压缩%s到%s中' % (src, dst))
        self.fout = tarfile.open(dst, 'w:gz')
        self.fout.add(src)
        self.fout.close()
        self.logTool.info('压缩完成')


    def decompress(self, gzFile, dst):
        self.fin = tarfile.open(gzFile, 'r:gz')
        self.fin.extractall(dst)
        self.fin.close()
