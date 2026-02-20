from models import Recipes, Ingredients, RecipeIngredients, KitchenTools, RecipeTools
from database import SessionLocal
from datetime import date
from sqlalchemy import select, func, desc


def create_full_recipe(name:str,
                       number_of_portions:int,
                       instructions:str,
                       ingredient_list:list,
                       tool_list:list|None=None,
                       meal_type:str|None=None,
                       notes:str|None=None,
                       nationality:str|None=None):
    """
    Creating compelete recipe with linkages to the needed ingredients and kitchen tools.
    Saving the changes permanently in the database.
    ingredient_list: [(ingredient_name, quantity, unit, component)]
    tool_list: [kitchen_tool_name]
    """

    session = SessionLocal()

    try:
        recipe_id = create_recipe(session, 
                                  name, 
                                  number_of_portions,
                                  instructions,
                                  meal_type,
                                  notes,
                                  nationality)
        
        for ingredient_name, quantity, unit, component in ingredient_list:
            add_ingredient_to_recipe(session, 
                                     recipe_id, 
                                     ingredient_name,
                                     quantity, 
                                     unit,
                                     component)
            
        for kitchen_tool_name in tool_list:
            add_tool_to_recipe(session, 
                               recipe_id,
                               kitchen_tool_name)
            
        session.commit()
        return recipe_id
    
    except:
        session.rollback()
        raise
    finally:
        session.close()


def create_recipe(session,
                  name:str,
                  number_of_portions:int,
                  instructions:str,
                  meal_type:str|None=None,
                  notes:str|None=None,
                  nationality:str|None=None):
    """
    Creating new recipe and saving it in the database.
    """

    # Create new Recipe
    new_recipe = Recipes(name = name,
                         number_of_portions = number_of_portions,
                         instructions = instructions,
                         meal_type = meal_type,
                         nationality = nationality,
                         notes = notes,
                         created_at = date.today())

    session.add(new_recipe)
    session.flush()

    return new_recipe.id


def add_ingredient_to_recipe(session,
                             recipe_id:int,
                             name:str,
                             quantity:float|None=None,
                             unit:str|None=None,
                             component:str|None=None):
    """
    Creating a new linkage between a recipe and an ingredient and saving it in the database.
    """

    ingredient = get_or_create_ingredient(session, name)

    new_recipe_ingredient = RecipeIngredients(recipe_id = recipe_id,
                                              ingredient_id = ingredient.id,
                                              quantity = quantity,
                                              unit = unit,
                                              component = component)
    
    session.add(new_recipe_ingredient)
    session.flush()


def add_tool_to_recipe(session,
                       recipe_id:int,
                       name:str):
    """
    Creating a new linkage between a recipe and a kitchen tool and saving it in the database.
    """

    kitchen_tool = get_or_create_kitchen_tool(session, name)

    new_recipe_tool = RecipeTools(recipe_id = recipe_id,
                                  tool_id = kitchen_tool.id)
    
    session.add(new_recipe_tool)
    session.flush()


def get_or_create_ingredient(session, name: str):
    """
    Getting ingredient object with the given name. Create it if it does not exist.
    """
    ingredient = session.execute(
        select(Ingredients)
        .where(Ingredients.name == name)
    ).scalar_one_or_none()

    if ingredient is None:
        ingredient = Ingredients(name=name)
        session.add(ingredient)
        session.flush() 

    return ingredient


def get_or_create_kitchen_tool(session, name: str):
    """
    Getting kitchen tool object with the given name. Create it if it does not exist.
    """
    tool = session.execute(
        select(KitchenTools).where(KitchenTools.name == name)
    ).scalar_one_or_none()

    if tool is None:
        tool = KitchenTools(name=name)
        session.add(tool)
        session.flush()

    return tool


def get_recipe_by_id(session, recipe_id: int):
    """
    Getting recipe with the given ID. 
    Returning None if it does not exist 
    """

    recipe = session.execute(
        select(Recipes).where(Recipes.id == recipe_id)
    ).scalar_one_or_none()
    
    return recipe


def get_recipe_ingredients(session, recipe_id: int):
    """
    Getting all ingredients of the recipe with the given ID.
    Returning a dictionary with the ingredient name as keys and {"quantity":qnt, "unit":u, "component": cmp} as values.
    Returning an empty dictionary if there are no ingredients listed for this recipe.
    Attention: No checking whether a recipe with the given ID exists!
    """

    ingredient_list = session.execute(
        select(Ingredients.name, 
               RecipeIngredients.quantity, 
               RecipeIngredients.unit,
               RecipeIngredients.component)
        .join(Ingredients,
               Ingredients.id == RecipeIngredients.ingredient_id)
        .where(RecipeIngredients.recipe_id == recipe_id)
    ).all()

    ingredients_dict = {}
    for name, qnt, u, cmp in ingredient_list:
        ingredients_dict[name] = {"quantity":qnt, "unit":u, "component": cmp}

    return ingredients_dict


def get_recipe_tools(session, recipe_id: int):
    """
    Getting a list of all tools of the recipe with the given ID.
    Returning an empty list if there are no tools listed for this recipe.
    Attention: No checking whether a recipe with the given ID exists!
    """

    tool_list = session.execute(
        select(KitchenTools.name)
        .select_from(RecipeTools)
        .join(KitchenTools,
               KitchenTools.id == RecipeTools.tool_id)
        .where(RecipeTools.recipe_id == recipe_id)
    ).scalars().all()

    return tool_list


def get_all_recipes():
    """
    Getting a list of all recipes in the database.
    """

    session = SessionLocal()

    recipe_list = session.execute(
        select(Recipes)
    ).scalars().all()

    session.close()

    return recipe_list


def get_full_recipe_by_id(recipe_id: int):
    """
    Getting the recipe to the given ID with its ingredients and needed kitchen tools.
    """
    
    session = SessionLocal()

    recipe = get_recipe_by_id(session, recipe_id)

    if recipe is None:
        return None
    
    ingredient_dict = get_recipe_ingredients(session, recipe_id)
    tool_list = get_recipe_tools(session, recipe_id)

    session.close()

    return {"recipe": recipe,
            "ingredients": ingredient_dict,
            "tools": tool_list}


def get_recipes_by_ingredients(ingredient_list: list):
    """
    Getting a list of recipes which contain all ingredients contained in the list.
    """

    session = SessionLocal()

    recipe_list = session.execute(
        select(Recipes)
        .join(Recipes.ingredients)
        .where(Ingredients.name.in_(ingredient_list))
        .group_by(Recipes.id)
        .having(func.count(func.distinct(Ingredients.id)) == len(ingredient_list))
    ).scalars().all()

    session.end()

    return recipe_list


def get_best_recipes_for_ingredients(ingredient_list: list):
    """
    Getting a list of recipes which contain at least one ingredient of the given list.
    Sorting the list descending by the number of matching ingredients.
    Output: [(Recipe, Number of matching ingredients)]
    """

    session = SessionLocal()

    recipe_list = session.execute(
        select(Recipes, 
               func.count(func.distinct(Ingredients.id)).label("matching_ingredients_count"))
        .join(Recipes.ingredients)
        .where(Ingredients.name.in_(ingredient_list))
        .group_by(Recipes.id)
        .order_by(desc("matching_ingredients_count"))
    ).all()

    session.close()

    return recipe_list


def get_best_recipes_for_ingredients_with_quantity(ingredient_list: list,
                                                   number_of_portions: int):
    """
    Getting a list of recipes which contain at least one ingredient of the given list.
    Sorting the list descending by the number of matching ingredients.
    Each recipe-dictionary in the output contains a dictionary with the matching ingredients and
    their needed amount for the given number of poortions.
    Output: [{Recipe, Number of matching ingredients, {ingredient: {quantity, unit}}}]
    """

    session = SessionLocal()

    recipe_ingredient_list = session.execute(
        select(Recipes, 
               func.count(func.distinct(Ingredients.id)).label("matching_ingredients_count"),
               Ingredients.name,
               RecipeIngredients.quantity * number_of_portions / Recipes.number_of_portions.label("scaled_quantity"), 
               RecipeIngredients.unit)
        .join(RecipeIngredients,
              RecipeIngredients.recipe_id == Recipes.id)
        .join(Ingredients,
              RecipeIngredients.ingredient_id == Ingredients.id)
        .where(Ingredients.name.in_(ingredient_list))
    ).all()

    session.close()

    recipe_map = {}
    for recipe, ing, qnt, u in recipe_ingredient_list:
        if not recipe.id in recipe_map.keys():
            recipe_map[recipe.id] = {"recipe": recipe, 
                                     "matching_ingredients_count": 0,
                                     "ingredients": {}}
            
        recipe_map[recipe.id]["matching_ingredients_count"] += 1
        recipe_map[recipe.id]["ingredients"][ing] = {"quantity": qnt, "unit": u}

    recipe_list = sorted(recipe_map.values(), key=lambda x: x["matching_count"], reverse=True)

    return recipe_list


def get_recipes_by_nationality(nationality: str):
    """
    Getting a list of recipes of the given nationality.
    """

    session = SessionLocal()

    recipe_list = session.execute(
        select(Recipes)
        .where(Recipes.nationality == nationality)
    ).scalars.all()

    session.end()

    return recipe_list


def get_recipes_by_meal_type(meal_type: str):
    """
    Getting a list of recipes of the given meal type.
    """

    session = SessionLocal()

    recipe_list = session.execute(
        select(Recipes)
        .where(Recipes.meal_type == meal_type)
    ).scalars.all()

    session.end()

    return recipe_list