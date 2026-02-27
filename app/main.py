from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
import app.crud as crud
import app.schemas as schemas

app = FastAPI(title="Recipe API")

@app.get("/")
def read_root_endpoint():
    return {"message": "Welcome to Recipe API!"}


@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeResponse)
def read_recipe_endpoint(recipe_id: int, db: Session = Depends(get_db)):
    recipe = crud.get_full_recipe_by_id(db, recipe_id)
    return recipe


@app.delete("/recipes/{recipe_id}", status_code=201)
def delete_recipe_by_id_endpoint(recipe_id: int, db: Session = Depends(get_db)):
    crud.delete_recipe_by_id(db, recipe_id)


@app.get("/recipes/all/{skip}", response_model=list[schemas.RecipeListResponse])
def read_all_recipes_endpoint(db: Session = Depends(get_db), 
                     skip: int = 0,
                     limit: int = 10):
    recipe_list = crud.get_all_recipes(db, skip, limit)
    return recipe_list


@app.get("/recipes/all/filtered", response_model=list[schemas.RecipeListResponse])
def read_filtered_recipes_endpoint(db: Session = Depends(get_db),
                          meal_types: list[str] = Query(default=None),
                          nationalities: list[str] = Query(default=None),
                          collections: list[int] = Query(default=None),
                          skip: int = 0,
                          limit: int = 10):
    recipe_list = crud.get_recipes_filtered(db, meal_types, nationalities, collections, skip, limit)
    return recipe_list


@app.post("/recipes/", response_model=schemas.RecipeCreateResponse, status_code=201)
def create_recipe_endpoint(recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    try:
        recipe_id = crud.create_full_recipe(db, recipe)
        return {"recipe_id": recipe_id}
   
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not create recipe: {str(e)}"
        )


@app.get("/collections/all", response_model=list[schemas.CollectionResponse])
def read_all_collections_endpoint(db: Session = Depends(get_db)):
    collections_list = crud.get_all_collections(db)
    return collections_list


@app.post("/collections/new", response_model=schemas.CollectionCreateResponse, status_code=201)
def create_collection_endpoint(collection: schemas.CollectionCreate, db: Session = Depends(get_db)):
    try:
        collection_id = crud.create_collection(db, collection)
        return {"collection_id": collection_id}
    
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not create collection: {str(e)}"
        )
    

@app.post("/collections/", status_code=201)
def add_recipe_to_collection_endpoint(recipe_id: int, collection_id: int, db: Session = Depends(get_db)):
    try:
        crud.add_recipe_to_collection(db, recipe_id, collection_id)
        return {"New recipe in collection."}

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not add recipe to collection: {str(e)}"
        )
    

