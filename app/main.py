from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import SessionLocal
from models import Recipes, RecipeIngredients, RecipeTools
from schemas import RecipeResponse
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal
from crud import create_full_recipe, get_full_recipe_by_id
from schemas import RecipeCreate, RecipeResponse, RecipeCreateResponse, IngredientResponse, ToolResponse

app = FastAPI(title="Recipe API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Recipe API!"}


@app.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def read_recipe(recipe_id: int):
    session = SessionLocal()
    try:
        recipe = get_full_recipe_by_id(session, recipe_id)
        return recipe
    finally:
        session.close()


@app.post("/recipes/", response_model=RecipeCreateResponse, status_code=201)
def create_recipe(recipe: RecipeCreate):
    """
    Creating a new recipe and saving it in the database.
    """
    session = SessionLocal()

    try:
        recipe_id = create_full_recipe(session, recipe)
        return {"recipe_id": recipe_id}
   
    except Exception as e:
        session.rollback()

        raise HTTPException(
            status_code=400,
            detail=f"Could not create recipe: {str(e)}"
        )

    finally:
        session.close()

    