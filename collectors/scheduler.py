from apscheduler.schedulers.background import BackgroundScheduler
from collectors.rss import collect_rss
from collectors.arxiv import collect_arxiv
from db.database import init_db


def run_collect():
    print("[Scheduler] 定期収集開始")
    init_db()
    collect_rss()
    collect_arxiv()
    print("[Scheduler] 定期収集完了")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # 毎朝7時に収集
    scheduler.add_job(run_collect, "cron", hour=7, minute=0, id="daily_collect")
    scheduler.start()
    print("[Scheduler] 毎朝7時の自動収集をスケジュールしました")
    return scheduler
