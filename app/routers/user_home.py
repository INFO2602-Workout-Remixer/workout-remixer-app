from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html",
        context={
            "user": user
        }
    )

@router.get("/app/dashboard", response_class=HTMLResponse)
async def dashboard_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html",
        context={
            "user": user
        }
    )

@router.get("/app/exercises", response_class=HTMLResponse)
async def exercises_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="exercises/index.html",
        context={
            "user": user
        }
    )

@router.get("/app/routines", response_class=HTMLResponse)
async def routines_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="routines/index.html",
        context={
            "user": user
        }
    )

@router.get("/app/community", response_class=HTMLResponse)
async def community_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="routines/community.html",
        context={
            "user": user
        }
    )

@router.get("/app/history", response_class=HTMLResponse)
async def history_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="workout/history.html",
        context={
            "user": user
        }
    )

@router.get("/app/routines/create", response_class=HTMLResponse)
async def create_routine_view(
    request: Request,
    user: AuthDep,
    db:SessionDep
):
    return templates.TemplateResponse(
        request=request, 
        name="routines/form.html",
        context={
            "user": user
        }
    )

@router.get("/app/routines/{routine_id}", response_class=HTMLResponse)
async def routine_detail_view(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    routine_id: int
):
    return templates.TemplateResponse(
        request=request, 
        name="routines/detail.html",
        context={
            "user": user,
            "routine_id": routine_id
        }
    )

@router.get("/app/routines/{routine_id}/edit", response_class=HTMLResponse)
async def routine_edit_view(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    routine_id: int
):
    return templates.TemplateResponse(
        request=request, 
        name="routines/form.html",
        context={
            "user": user,
            "routine_id": routine_id
        }
    )

@router.get("/app/workout/active/{routine_id}", response_class=HTMLResponse)
async def active_workout_view(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    routine_id: int
):
    return templates.TemplateResponse(
        request=request, 
        name="workout/active.html",
        context={
            "user": user,
            "routine_id": routine_id
        }
    )