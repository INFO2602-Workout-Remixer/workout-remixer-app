from fastapi import APIRouter
from app.dependencies import SessionDep, AuthDep
from app.models.routine import Routine

router = APIRouter(prefix="/routines", tags=["Routines"])

@router.get("/")
async def get_routines(db: SessionDep, user: AuthDep):
    routines = db.exec(select(Routine).where(Routine.user_id == user.id)).all()
    return routines