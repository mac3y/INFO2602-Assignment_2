from fastapi import APIRouter, Request, Form
from sqlmodel import select
from app.database import SessionDep
from app.models import Pokemon, UserPokemon
from app.auth import AuthDep
from app.utilities.flash import flash
from fastapi.responses import RedirectResponse
from fastapi import status
from typing import Annotated

capture_router = APIRouter(tags=["Capture"])

@capture_router.post("/capture")
async def capture_pokemon(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    pokemon_id: Annotated[int, Form()],
    name: Annotated[str, Form()]
):

    existing=db.exec(select(UserPokemon).where(UserPokemon.user_id==user.id, UserPokemon.pokemon_id==pokemon_id)).first()

    if existing:
        flash(request, "You already caught this Pokemon!", "warning")
    else:
        captured=UserPokemon(
            user_id=user.id,
            pokemon_id=pokemon_id,
            nickname=name if name else None
        )
        print(f"SAVED: Pokemon ID {pokemon_id} with nickname '{name}'")
        db.add(captured)
        db.commit()
        flash(request, "Successfully captured Pokemon!", "success")
    
    return RedirectResponse(url="/mypokemon", status_code=status.HTTP_303_SEE_OTHER)