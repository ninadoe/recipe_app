from app.models import Recipes, Ingredients, RecipeIngredients, KitchenTools, RecipeTools, RecipeCollections, Collections
from datetime import date
from sqlalchemy import select, func, desc, delete
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from app.schemas import RecipeCreate, CollectionCreate

"""
RECIPES
"""

def create_full_recipe(session,
                       recipe: RecipeCreate) -> int:
    """
    Creating compelete recipe with linkages to the needed ingredients and kitchen tools.
    Saving the changes permanently in the database.
    """

    try:
        recipe_id = create_recipe(session=session, 
                                name=recipe.name, 
                                number_of_portions=recipe.number_of_portions,
                                instructions=recipe.instructions,
                                meal_type=recipe.meal_type,
                                notes=recipe.notes,
                                nationality=recipe.nationality)
        
        for ingredient in recipe.ingredients:
            add_ingredient_to_recipe(session, 
                                    recipe_id, 
                                    ingredient.name,
                                    ingredient.quantity, 
                                    ingredient.unit,
                                    getattr(ingredient, "component", None))
            
        for kitchen_tool in recipe.tools:
            add_tool_to_recipe(session, 
                                recipe_id,
                                kitchen_tool.name)

        session.commit()
        return recipe_id
    
    except Exception as e:
        session.rollback()
        raise ValueError(f"Could not create recipe: {str(e)}")



def create_recipe(session,
                  name:str,
                  number_of_portions:int,
                  instructions:str,
                  meal_type:str|None=None,
                  notes:str|None=None,
                  nationality:str|None=None) -> int:
    """
    Creating new recipe and saving it in the database.
    """

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


def get_full_recipe_by_id(session, recipe_id: int) -> Recipes:
    """
    Returning a Recipe object with ingredients and tools loaded.
    Raising HTTPException(404) if not found.
    """

    recipe = (
        session.query(Recipes)
        .options(
            joinedload(Recipes.ingredients).joinedload(RecipeIngredients.ingredient),
            joinedload(Recipes.tools).joinedload(RecipeTools.tool)
        )
        .filter(Recipes.id == recipe_id)
        .first()
    )

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    return recipe


def get_all_recipes(session, skip: int = 0, limit: int = 10) -> list[Recipes]:
    """
    Returning a list of all recipes in the database.
    The number of returned recipes is limited 
    and the first recipes in the database can be skipped.
    """

    recipe_list = session.query(Recipes).offset(skip).limit(limit).all()

    return recipe_list


def get_recipes_filtered(session,
                         meal_types: list[str] | None = None,
                         nationalities: list[str] | None = None,
                         collections: list[str] | None = None,
                         skip: int = 0,
                         limit: int = 10) -> list[Recipes]:
    """
    Returning a list of all recipes matching the given filters.
    The number of returned recipes is limited 
    and the first recipes in the database can be skipped.
    """

    query = session.query(Recipes)

    if meal_types:
        query = query.filter(Recipes.meal_type.in_(meal_types))
    
    if nationalities:
        query = query.filter(Recipes.nationality.in_(nationalities))

    if collections:
        query = query.filter(Recipes.collections.in_(collections))

    return query.offset(skip).limit(limit).all()


def delete_recipe_by_id(session, recipe_id: int):
    """
    Removing the recipe with the given ID from the database.
    """

    recipe = session.get(Recipes, recipe_id)

    if not recipe:
        return False

    session.delete(recipe)
    session.flush()

    delete_not_used_ingredients(session)

    session.commit()

"""
COLLECIONS
"""

def create_collection(session, collection: CollectionCreate) -> int:
    """
    Creating a new Collection.
    """

    new_collection = Collections(name=collection.name)
    session.add(new_collection)
    session.commit()

    return new_collection.id


def add_recipe_to_collection(session,
                             recipe_id:int,
                             collection_id:int):
    """
    Creating a new linkage between a recipe and a collection and saving it in the database.
    """

    new_recipe_collection = RecipeCollections(recipe_id = recipe_id,
                                              collection_id = collection_id)
    
    session.add(new_recipe_collection)
    session.commit()


def get_all_collections(session) -> list[Collections]:
    """
    Returning all collections from the database.
    """

    collection_list = session.query(Collections).all()
    return collection_list

"""
INGREDIENTS
"""

def get_or_create_ingredient(session, name: str) -> Ingredients:
    """
    Returning ingredient object with the given name. 
    Creating it if it does not exist.
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


def delete_not_used_ingredients(session):
    """
    Removing all ingredients from the database which are not used in any recipe anymore.
    """

    ingredients_in_recipes = session.query(RecipeIngredients.ingredient_id)
    session.query(Ingredients
                  ).filter(~Ingredients.id.in_(ingredients_in_recipes)
                  ).delete(synchronize_session=False)
    
    session.flush

"""
KItCHENTOOLS
"""

def get_or_create_kitchen_tool(session, name: str) -> KitchenTools:
    """
    Returning kitchen tool object with the given name. 
    Creating it if it does not exist.
    """
    tool = session.execute(
        select(KitchenTools).where(KitchenTools.name == name)
    ).scalar_one_or_none()

    if tool is None:
        tool = KitchenTools(name=name)
        session.add(tool)
        session.flush()

    return tool
















def get_recipes_by_ingredients(session, ingredient_list: list):
    """
    Getting a list of recipes which contain all ingredients contained in the list.
    """

    recipe_list = session.execute(
        select(Recipes)
        .join(Recipes.ingredients)
        .where(Ingredients.name.in_(ingredient_list))
        .group_by(Recipes.id)
        .having(func.count(func.distinct(Ingredients.id)) == len(ingredient_list))
    ).scalars().all()

    return recipe_list


def get_best_recipes_for_ingredients(session, ingredient_list: list):
    """
    Getting a list of recipes which contain at least one ingredient of the given list.
    Sorting the list descending by the number of matching ingredients.
    Output: [(Recipe, Number of matching ingredients)]
    """

    recipe_list = session.execute(
        select(Recipes, 
               func.count(func.distinct(Ingredients.id)).label("matching_ingredients_count"))
        .join(Recipes.ingredients)
        .where(Ingredients.name.in_(ingredient_list))
        .group_by(Recipes.id)
        .order_by(desc("matching_ingredients_count"))
    ).all()

    return recipe_list


def get_best_recipes_for_ingredients_with_quantity(session,
                                                   ingredient_list: list,
                                                   number_of_portions: int):
    """
    Getting a list of recipes which contain at least one ingredient of the given list.
    Sorting the list descending by the number of matching ingredients.
    Each recipe-dictionary in the output contains a dictionary with the matching ingredients and
    their needed amount for the given number of poortions.
    Output: [{Recipe, Number of matching ingredients, {ingredient: {quantity, unit}}}]
    """

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


def get_recipes_by_nationality(session, nationality: str):
    """
    Getting a list of recipes of the given nationality.
    """

    recipe_list = session.execute(
        select(Recipes)
        .where(Recipes.nationality == nationality)
    ).scalars.all()

    return recipe_list


def get_recipes_by_meal_type(session, meal_type: str):
    """
    Getting a list of recipes of the given meal type.
    """

    recipe_list = session.execute(
        select(Recipes)
        .where(Recipes.meal_type == meal_type)
    ).scalars.all()

    return recipe_list


