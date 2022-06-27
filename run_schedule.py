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
        minutes = cfg.sources.dict()[source].get('minutes', None)
        seconds = cfg.sources.dict()[source].get('seconds', None)
        at_minutes = cfg.sources.dict()[source].get('at_minutes', None)
        if seconds is not None:
            schedule.every(seconds).seconds.do(run_job, source, receivers)
            print(f'<{source}> will run every {seconds}s seconds')
        elif minutes is not None:
            schedule.every(minutes).minutes.do(run_job, source, receivers)
            print(f'<{source}> will run every {minutes}m, with {receivers}')
        elif at_minutes is not None:
            schedule_at_minutes(at_minutes, run_job, (source, receivers))   
        else:
            raise Exception(f'Timing for <{source}> not defined')
            
    if cfg.tasks is not None:
        for source in cfg.tasks.list():
            task_name = cfg.tasks.dict()[source]['task']
            minutes = cfg.tasks.dict()[source].get('minutes', None)
            at_minutes = cfg.tasks.dict()[source].get('at_minutes', None)
            if minutes is None:
                schedule_at_minutes(at_minutes, run_task, (source, task_name))
                print(f'<{source}.{task_name}> will run every hour at {at_minutes}')
            else:
                schedule.every(minutes).minutes.do(run_task, source, task_name)
                print(f'<{source}.{task_name}> will run every {minutes}m')
            
def schedule_at_minutes(at_minutes, fn, args):
    for at_minute in at_minutes:
        at_minute_str = f':{str(at_minute).zfill(2)}'
        schedule.every().hour.at(at_minute_str).do(fn, *args)   
        print(f'<{args}> will run every hour at {at_minute_str}')
        
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
