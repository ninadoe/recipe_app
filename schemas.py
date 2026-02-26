from pydantic import BaseModel
from typing import List
from datetime import datetime
from models import RecipeIngredients, RecipeTools


class IngredientCreate(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None
    component: str | None = None


class ToolCreate(BaseModel):
    name: str


class RecipeCreate(BaseModel):
    name: str
    number_of_portions: int
    instructions: str
    nationality: str | None = None
    meal_type: str | None = None
    notes: str | None = None
    ingredients: List[IngredientCreate]
    tools: List[ToolCreate]


class RecipeCreateResponse(BaseModel):
    recipe_id: int


class IngredientResponse(BaseModel):
    name: str
    quantity: float | None
    unit: str | None
    component: str | None

    model_config = {
        "from_attributes": True
    }


class ToolResponse(BaseModel):
    name: str

    model_config = {
        "from_attributes": True
    }


class RecipeResponse(BaseModel):
    id: int
    name: str
    number_of_portions: int
    instructions: str
    nationality: str | None
    meal_type: str | None
    notes: str | None
    created_at: datetime
    ingredients: list[IngredientResponse]
    tools: list[ToolResponse]

    model_config = {
        "from_attributes": True
    }

