from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import select
from app.database import SessionDep
from app.models import UserPokemon, Pokemon
from app.auth import AuthDep
from app.utilities.flash import flash
from typing import Optional, Annotated
from fastapi import status
from . import templates

mypokemon_router = APIRouter(tags=["My Pokemon"])

@mypokemon_router.get("/mypokemon", response_class=HTMLResponse)
async def my_pokemon(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    q: Optional[str] = Query(default=None)
):
    
    query=select(UserPokemon, Pokemon).join(Pokemon, UserPokemon.pokemon_id==Pokemon.id).where(UserPokemon.user_id==user.id)

    if q:
        query=query.where(
            (Pokemon.name.ilike(f"%{q}%")) |
            (UserPokemon.nickname.ilike(f"%{q}%"))
        )

    results=db.exec(query).all()

    captured_pokemon=[]
    for user_pokemon, pokemon in results:
        captured_pokemon.append({
            "id": user_pokemon.id,
            "nickname": user_pokemon.nickname or pokemon.name,
            "pokemon_name": pokemon.name,
            "weight": pokemon.weight,
            "height": pokemon.height,
            "image_url": pokemon.image_url
        })

    print(f"User {user.id} has {len(captured_pokemon)} captured Pokemon")
    
    print(f"Captured Pokemon data: {captured_pokemon}")
    
    return templates.TemplateResponse(
        request=request,
        name="mypokemon.html",
        context={
            "user": user,
            "captured_pokemon": captured_pokemon,
            "q": q or ""
        }
    )


@mypokemon_router.put("/mypokemon/{user_pokemon_id}/rename")
@mypokemon_router.post("/mypokemon/{user_pokemon_id}/rename")
async def rename_pokemon(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    user_pokemon_id: int,
    name: Annotated[str, Form()],
    method_override: Optional[str] = Form(default=None)
):

    print(f"*** RENAME ENDPOINT HIT for ID {user_pokemon_id} with name '{name}' ***")
    captured = db.get(UserPokemon, user_pokemon_id)
    if captured and captured.user_id==user.id:
        captured.nickname=name
        db.add(captured)
        db.commit()
        flash(request, "Successfully renamed Pokemon!", "success")
        print(f"*** RENAME SUCCESS ***")
    else:
        flash(request, "Pokemon not found!", "danger")
        print(f"*** RENAME FAILED: Pokemon not found ***")

    return RedirectResponse(url="/mypokemon", status_code=status.HTTP_303_SEE_OTHER)


@mypokemon_router.delete("/mypokemon/{user_pokemon_id}/release")
@mypokemon_router.post("/mypokemon/{user_pokemon_id}/release")
async def release_pokemon(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    user_pokemon_id: int,
    method_override: Optional[str] = Form(default=None)
):
    captured=db.get(UserPokemon, user_pokemon_id)
    if captured and captured.user_id==user.id:
        db.delete(captured)
        db.commit()
        flash(request, "Bye bye", "info")
    else:
        flash(request, "Pokemon not found!", "danger")

    return RedirectResponse(url="/mypokemon", status_code=status.HTTP_303_SEE_OTHER)