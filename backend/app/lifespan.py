from app.scheduler.schedule_manager import ScheduleManager
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Setup schedule manager
scheduler_manager = ScheduleManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await scheduler_manager.start()
    print("Scheduler started.")
    yield
    scheduler_manager.scheduler.shutdown(wait=False)
    print("Scheduler stopped.")