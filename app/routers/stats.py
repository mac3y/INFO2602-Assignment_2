from fastapi import APIRouter, Request
from sqlmodel import select, func
from app.database import SessionDep
from app.models import UserPokemon, Pokemon
from app.auth import AuthDep
from fastapi.responses import HTMLResponse
from . import templates

stats_router = APIRouter(tags=["Stats"])

@stats_router.get("/stats", response_class=HTMLResponse)
async def stats_page(
    request: Request,
    user: AuthDep,
    db: SessionDep
):
    query=select(Pokemon.name, func.count(UserPokemon.id)).join(
        UserPokemon, UserPokemon.pokemon_id == Pokemon.id
    ).where(UserPokemon.user_id == user.id).group_by(Pokemon.name)

    results = db.exec(query).all()
    chart_data = [{"name": name, "y": count} for name, count in results]

    if not chart_data:
        chart_data = [{"name": "No Pokemon", "y": 1}]

    return templates.TemplateResponse(
        request=request,
        name="stats.html",
        context={"user": user, "chart_data": chart_data}
    )