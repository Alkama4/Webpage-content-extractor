from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.utils import get_aiomysql_connection, execute_mysql_query
from app.scraper.utils import run_scrape


class ScheduleManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        await self.load_schedules_from_db()
        self.scheduler.start()

    async def load_schedules_from_db(self):
        async with get_aiomysql_connection() as conn:
            rows = await execute_mysql_query(conn, "SELECT * FROM webpages")
            for row in rows:
                await self._sync_schedule(row)

    async def _sync_schedule(self, row: dict):
        job_id = f"webpage_{row['webpage_id']}"
        self.scheduler.remove_job(job_id, jobstore=None, job_defaults=None, replace_existing=False) if self.scheduler.get_job(job_id) else None

        if row["is_active"]:
            trigger = CronTrigger(hour=row["run_hour"], minute=row["run_minute"])
            self.scheduler.add_job(self._run_webpage_job, trigger, id=job_id, args=[row], replace_existing=True)

    async def update_schedule(self, webpage_id: int):
        async with get_aiomysql_connection() as conn:
            row = await execute_mysql_query(conn, "SELECT * FROM webpages WHERE webpage_id=%s", (webpage_id,))
            if row:
                await self._sync_schedule(row[0])

    async def remove_schedule(self, webpage_id: int):
        job_id = f"webpage_{webpage_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

    async def add_schedule(self, webpage_id: int):
        await self.update_schedule(webpage_id)

    def list_jobs(self) -> list[dict]:
        """
        Returns a list of all scheduled jobs with basic details.
        """
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "func_name": job.func_ref,
                "args": job.args
            })
        return jobs_info

    async def _run_webpage_job(self, row: dict):
        print(f"Running job for webpage: {row['page_name']} ({row['url']})")
        await run_scrape(row['webpage_id'])        
