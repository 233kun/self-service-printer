import logging
import os.path
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import setting
from models import GetJobsAccessLogFilter
from routers import user, printer
from routers import pay
from automatic_tasks import startup, clean_expired_directories, clear_expired_bills

ml_models = {}
logging.getLogger('apscheduler.executors.default').propagate = False


# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()  # startup task
    scheduler = BackgroundScheduler()
    scheduler.add_job(clean_expired_directories, 'interval', seconds=5, )  # auto remove expired directory
    scheduler.add_job(clear_expired_bills, 'interval', seconds=5, )
    scheduler.start()
    yield
    ml_models.clear()

if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('pending_files'):
    os.makedirs('pending_files')
app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(user.router)
app.include_router(pay.router)
app.include_router(printer.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.ORIGIN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logging.getLogger("uvicorn.access").addFilter(GetJobsAccessLogFilter())

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
