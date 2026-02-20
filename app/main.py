from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal
from crud import get_full_recipe_by_id, add_ingredient_to_recipe, add_tool_to_recipe, create_recipe

app = FastAPI(title="Recipe API")

class IngredientIn(BaseModel):
    name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None

class RecipeIn(BaseModel):
    name: str
    number_of_portions: int
    instructions: str
    ingredients: List[IngredientIn]
    tools: List[str] = []
    meal_type: Optional[str] = None
    nationality: Optional[str] = None
    notes: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Recipe API!"}

@app.get("/recipes/{recipe_id}")
def read_recipe(recipe_id: int):
    session = SessionLocal()
    result = get_full_recipe_by_id(session, recipe_id)
    session.close()

    if result is None:
        return {"error": "Recipe not found"}

    from schemas import serialize_recipe
    return serialize_recipe(result)


@app.post("/recipes/")
def create_full_recipe(recipe: RecipeIn):
    session = SessionLocal()

    recipe_id = create_recipe(session,
                              name=recipe.name,
                              number_of_portions=recipe.number_of_portions,
                              instructions=recipe.instructions,
                              meal_type=recipe.meal_type,
                              nationality=recipe.nationality,
                              notes=recipe.notes)

    # Zutaten hinzufügen
    for ing in recipe.ingredients:
        add_ingredient_to_recipe(session,
                                 recipe_id,
                                 name=ing.name,
                                 quantity=ing.quantity,
                                 unit=ing.unit)

    # Tools hinzufügen
    for tool in recipe.tools:
        add_tool_to_recipe(session, recipe_id, name=tool)

    session.commit()
    session.close()

    return {"recipe_id": recipe_id}