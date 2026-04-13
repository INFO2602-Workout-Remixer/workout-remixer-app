from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.utilities.flash import get_flashed_messages
from jinja2 import Environment, FileSystemLoader
from app.config import get_settings
from app.api import exercises_router, routines_router, dashboard_router, workouts_router

template_env = Environment(loader = FileSystemLoader("app/templates"), )
template_env.globals['get_flashed_messages'] = get_flashed_messages
templates = Jinja2Templates(env=template_env)
static_files = StaticFiles(directory="app/static")

router = APIRouter(tags=["Jinja Based Endpoints"], include_in_schema=get_settings().env.lower() in ["dev","development"])
api_router = APIRouter(tags=["API Endpoints"], prefix="/api")

api_router.include_router(exercises_router)
api_router.include_router(routines_router)
api_router.include_router(dashboard_router)
api_router.include_router(workouts_router)

from . import (index, login, register, admin_home, user_home, users, logout)