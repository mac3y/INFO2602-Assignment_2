from sqlmodel import SQLModel, Field
from typing import Optional

class UserPokemon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    pokemon_id: int = Field(foreign_key="pokemon.id")
    nickname: str = Field(max_length=225)