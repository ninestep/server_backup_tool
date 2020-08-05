import log, os, hashlib
from back_up import FullBack
from Tools import Config, FileEventHandler
from send import Mail, Baidu
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from watchdog.observers import Observer

logTool = log.logs()
conf = Config()
sched = BlockingScheduler()


def main():
    config = conf.getConfig()
    save_path = config['default']['save_path']
    keys = config['back_up'].keys()
    logTool.info('找的%d个备份设置' % (len(keys)))
    file_keys = ['path']
    database_keys = ['address', 'database', 'port', 'username', 'password']
    # 校验配置是否完整
    logTool.info('开始检查配置...')
    for (k, v) in config['back_up'].items():
        if 'type' not in v:
            logTool.error('%s配置下没有设置备份类型' % k)
            raise ValueError('%s配置下没有设置备份类型' % k)
        if v['type'] == 'file':
            keys = file_keys
        else:
            keys = database_keys
        for x in keys:
            if x not in v.keys():
                logTool.error('%s配置下缺少配置%s' % (k, x))
                raise ValueError('%s配置下缺少配置%s' % (k, x))
    logTool.info('配置检查完成，开始备份...')
    observer = Observer()
    for (k, v) in config['back_up'].items():
        fullBack(k, v, save_path)
        if v['type'] == 'file' and v['backup_type'] == 'increment':
            logTool.info('为%s配置增量备份定时任务' % k)
            event_handler = FileEventHandler(k)
            logTool.info('增量监听路径为%s' % v['path'])
            observer.schedule(event_handler, os.path.realpath(v['path']), True)
            sched.add_job(fullBack, CronTrigger.from_crontab(v['cron']), args=[k, v, event_handler.get_save_path()])
        else:
            logTool.info('为%s配置全量备份定时任务' % k)
            sched.add_job(fullBack, CronTrigger.from_crontab(v['cron']), args=[k, v, save_path])

    logTool.info('文件监听开始工作')
    observer.start()
    logTool.info('定时任务监听开始工作')
    sched.start()
    observer.join()


def fullBack(name, args, save_path):
    # 首次运行进行全局备份
    file_back = FullBack(save_path)
    logTool.info('开始备份%s' % (name))
    save_path = file_back.BackUp(name, args['type'], args)
    save_type = conf.get('save')
    if args['save_name'] not in save_type.keys():
        logTool.error('%s配置设置了不存在的保存方式%s' % (name, args['save_name']))
        raise ValueError('%s配置设置了不存在的保存方式%s' % (name, args['save_name']))
    try:
        save_conf = save_type[args['save_name']]
        save = {"Mail": Mail, "Baidu": Baidu}[save_conf['type']]()
        save.save(save_path, name)
    except Exception as e:
        logTool.error('%s文件上传出错，错误信息：%s' % (name, e))
    finally:
        os.remove(save_path)


if __name__ == '__main__':
    main()
