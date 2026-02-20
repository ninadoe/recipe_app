def serialize_recipe(full_recipe: dict):
    """
    Returning all properties of the given recipe in a dictionary.
    Input: {"recipe": Recipe, "ingredients": dict, "tools": list}
    """

    recipe = full_recipe["recipe"]
    ingredients = full_recipe["ingredients"]
    tools = full_recipe["tools"]

    return {"name": recipe.name,
            "number_of_portions": recipe.number_of_portions,
            "instructions": recipe.instructions,
            "ingredients": ingredients,
            "tools": tools,
            "nationality": recipe.nationality,
            "meal_type": recipe.meal_type,
            "notes": recipe.notes,
            "created_at": recipe.created_at.isoformat()}