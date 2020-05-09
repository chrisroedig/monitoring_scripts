import time
import schedule
import config
import run_once
import task

def init():
    cfg = config.Config().schedule
    if cfg is None:
        raise Exception('Schedule is not defined in the config')

    for source in cfg.sources.list():
        receivers = cfg.sources.dict()[source]['receivers']
        minutes = cfg.sources.dict()[source]['minutes']
        schedule.every(minutes).minutes.do(run_job, source, receivers)
        print(f'<{source}> will run every {minutes}m, with {receivers}')

    for source in cfg.tasks.list():
        task_name = cfg.tasks.dict()[source]['task']
        minutes = cfg.tasks.dict()[source]['minutes']
        schedule.every(minutes).minutes.do(run_task, source, task_name)
        print(f'<{source}.{task_name}> will run every {minutes}m')

def run_job(source, receivers):
    print(f'Runnning <{source}> with {receivers}')
    try:
        run_once.run(source, receivers)
        print(f'Finished runnning <{source}>')
    except:
        print(f'Exception while running <{source}>')

def run_task(source, task_name):
    print(f'Runnning <{source}.{task_name}>')
    try:
        task.run(source, task_name)
        print(f'Finished runnning <{source}.{task_name}>')
    except:
        print(f'Exception while running <{source}.{task_name}>')


def run():
    while True:
      schedule.run_pending()
      time.sleep(1)
 
if __name__ == '__main__':
    print('Initializing Schedule')
    init()
    print('Running Schedule')
    run()
    print('Exiting')
