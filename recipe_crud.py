from models import Recipes, Ingredients, RecipeIngredients, KitchenTools, RecipeTools
from database import SessionLocal
from datetime import date
from sqlalchemy import select


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
    ingredient_list: [(ingredient_name, quantity, unit)]
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
        
        for ingredient_name, quantity, unit in ingredient_list:
            add_ingredient_to_recipe(session, 
                                     recipe_id, 
                                     ingredient_name,
                                     quantity, 
                                     unit)
            
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
                             unit:str|None=None):
    """
    Creating a new linkage between a recipe and an ingredient and saving it in the database.
    """

    ingredient = get_or_create_ingredient(session, name)

    new_recipe_ingredient = RecipeIngredients(recipe_id = recipe_id,
                                              ingredient_id = ingredient.id,
                                              quantity = quantity,
                                              unit = unit)
    
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
    Get ingredient object with the given name. Create it if it does not exist.
    """
    ingredient = session.execute(
        select(Ingredients).where(Ingredients.name == name)
    ).scalar_one_or_none()

    if ingredient is None:
        ingredient = Ingredients(name=name)
        session.add(ingredient)
        session.flush() 

    return ingredient


def get_or_create_kitchen_tool(session, name: str):
    """
    Get kitchen tool object with the given name. Create it if it does not exist.
    """
    tool = session.execute(
        select(KitchenTools).where(KitchenTools.name == name)
    ).scalar_one_or_none()

    if tool is None:
        tool = KitchenTools(name=name)
        session.add(tool)
        session.flush()

    return tool
