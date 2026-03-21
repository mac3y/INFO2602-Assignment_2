from fastapi import APIRouter, HTTPException, Depends, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import *
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional
from fastapi import status
from . import templates

pokemon_router = APIRouter()

@pokemon_router.get("/pokemon", response_class=HTMLResponse)
async def pokemon(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    q: Optional[str] = Query(default=None)
):
    query=select(Pokemon)
    if q:
        query=query.where(Pokemon.name.ilike(f"%{q}%"))

    pokemons=db.exec(query).all()

    return templates.TemplateResponse(
        request=request, 
        name="pokemon.html",
        context={
            "user": user,
            "pokemons": pokemons,
            "q": q or ""
        }
    )