from app.models import Pokemon, User
import typer
import csv
from tabulate import tabulate
from sqlmodel import select
from app.database import create_db_and_tables, get_cli_session, drop_all
from app.models import *
from app.auth import encrypt_password
import subprocess
import platform
import os

cli = typer.Typer()

@cli.command()
def initialize():
    """Initialize the database with POkemon data"""
    print("Initializing database...")

    create_db_and_tables()
    print("Tables created")

    csv_file='pokemon.csv'
    if not os.path.exists(csv_file):
        print(f"{csv_file} not found!")
        return
    
    with get_cli_session() as db:
        count=0
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader=csv.DictReader(file)

            for row in csv_reader:
                existing=db.exec(select(Pokemon).where(Pokemon.name==row['name'])).first()

                if not existing:
                    weight_val=row['weight_kg'].strip() if row['weight_kg'] else ''
                    height_val=row['height_m'].strip() if row['height_m'] else ''

                    pokemon = Pokemon(
                        name=row['name'],
                        weight=float(weight_val) if weight_val else 0.0,
                        height=float(height_val) if height_val else 0.0,
                        image_url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{row['pokedex_number']}.png"
                    )
                    db.add(pokemon)
                    count += 1
        db.commit()
        print(f"Added {count} Pokemon to database")

        existing_user=db.exec(select(User).where(User.username=="testuser")).first()
        if not existing_user:
            test_user=User(
                username="testuser",
                email="test@example.com",
                password=encrypt_password("testpass"),
                role="user"
            )
            db.add(test_user)
            db.commit()
            print("Create test user (username: testuser, password: testpass)")

    with get_cli_session() as db:
        total=db.exec(select(Pokemon)).all()
        print(f"Total Pokemon in database: {len(total)}")
    print("Database initialization complete!")



@cli.command()
def test(base_url: str = "http://127.0.0.1:8000", headless: bool = True):
    try:
        subprocess.run(["npm", "install"], check=True, shell=platform.system() == "Windows")
    except subprocess.CalledProcessError:
        typer.secho("Installing test package failed. Install Node/npm on your PC to continue", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    try:
        env = os.environ.copy()
        env["BASE_URL"] = base_url
        env["HEADLESS"] = str(headless).lower()
        subprocess.run(["npm", "test"], check=True, shell=platform.system() == "Windows", env=env)
    except subprocess.CalledProcessError:
        typer.secho("Tests failed!", fg=typer.colors.RED)
        raise typer.Exit(code=1)
   
if __name__ == "__main__":
    cli()