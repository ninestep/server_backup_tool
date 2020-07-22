import yaml, shutil
from watchdog.observers import Observer
from watchdog.events import *
from datetime import datetime
from log import logs

logTool = logs()


class Config:
    def __init__(self, path='config.yaml'):
        self.path = path

    def getConfig(self):
        with open(self.path) as fp:
            con = fp.read()
        return yaml.safe_load(con)

    def get(self, name):
        with open(self.path) as fp:
            con = fp.read()
        config_dict = yaml.safe_load(con)
        if name in config_dict.keys():
            return config_dict[name]
        else:
            raise ValueError('未找到指定配置')


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, name):
        FileSystemEventHandler.__init__(self)
        self.name = name
        conf = Config()
        default_conf = conf.get('default')
        save_path = default_conf['save_path']
        self.save_path = os.path.join(save_path, name)
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path)
        self.log_path = os.path.join(self.save_path, 'log.txt')

    def get_save_path(self):
        return self.save_path

    def _save_log(self, file_name, action):
        """
        日志记录
        :param file_name: 文件名
        :param action: 动作，add新增，del删除，modified修改
        :return:
        """
        dt = datetime.now()

        with open(self.log_path, 'a') as fp:
            fp.write('%s\t%s\t%s\r\n' % (dt.strftime('%Y-%m-%d %H:%M:%S %f'), file_name, action))

    def _copy_file(self, file_path):
        real_path = os.path.realpath(file_path)
        if not os.path.isfile(real_path):
            logTool.error('%s未找到' % file_path)
        if file_path[0] == '/':
            save_path = file_path[1:]
        else:
            save_path = file_path
        to_path = os.path.join(self.save_path, save_path)
        [dirname, filename] = os.path.split(to_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        logTool.info('from %s copy to %s' % (real_path, to_path))
        shutil.copy(real_path, to_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._save_log(event.src_path, 'del')
            self._save_log(event.dest_path, 'add')
            self._copy_file(event.dest_path)

    def on_created(self, event):
        if not event.is_directory:
            self._save_log(event.src_path, 'add')
            self._copy_file(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._save_log(event.src_path, 'del')

    def on_modified(self, event):
        if not event.is_directory:
            self._save_log(event.src_path, 'modified')
            self._copy_file(event.src_path)
