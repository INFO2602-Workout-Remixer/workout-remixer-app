from app.api.exercises import router as exercises_router
from app.api.routines import router as routines_router
from app.api.dashboard import router as dashboard_router
from app.api.workouts import router as workouts_router

__all__ = ["exercises_router", "routines_router", "dashboard_router", "workouts_router"]