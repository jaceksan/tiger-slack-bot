from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime


def tick():
    print("Tick. The time is: %s" % datetime.now())

if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="Europe/Prague")
    scheduler.add_job(tick, 'interval', seconds=5)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass