from models import Recipes

def serialize_recipe(recipe: Recipes, 
                     ingredients: dict,
                     tools: list):
    """
    Returning all properties of the given recipe in a dictionary.
    """

    return {"name": recipe.name,
            "number_of_portions": recipe.number_of_portions,
            "instructions": recipe.instructions,
            "ingredients": ingredients,
            "tools": tools,
            "nationality": recipe.nationality,
            "meal_type": recipe.meal_type,
            "notes": recipe.notes,
            "created_at": recipe.created_at.isoformat()}