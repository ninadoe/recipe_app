from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

# Master Tables

class KitchenTools(Base):
    __tablename__ = "kitchen_tools"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    given = Column(Boolean, default=False)
    
    recipes = relationship("RecipeTools", back_populates="tool", cascade="all, delete-orphan")
    
class Ingredients(Base):
	__tablename__ = "ingredients"
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	
	recipes = relationship("RecipeIngredients", back_populates="ingredient", cascade="all, delete-orphan")    
     
class Collections(Base):
     __tablename__ = "collections"
     id = Column(Integer, primary_key=True)
     name = Column(String, nullable=False)

     recipes = relationship("RecipeCollections", back_populates="collection", cascade="all, delete-orphan")
	
# Main Table	
	
class Recipes(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    number_of_portions = Column(Integer, nullable=False)
    instructions = Column(Text, nullable=False)
    created_at = Column(Date, nullable=False)
    meal_type = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)

    ingredients = relationship("RecipeIngredients", back_populates="recipe", cascade="all, delete-orphan")
    ingredient_names = association_proxy("ingredients", "ingredient.name")

    tools = relationship("RecipeTools", back_populates="recipe", cascade="all, delete-orphan")
    tool_names = association_proxy("tools", "tool.name")

    collections = relationship("RecipeCollections", back_populates="recipe", cascade="all, delete-orphan")
    collection_names = association_proxy("collections", "collection.name")
	

# Connection Tables

class RecipeTools(Base):
    __tablename__ = "recipe_tools"
    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("kitchen_tools.id"), primary_key=True)
    
    recipe = relationship("Recipes", back_populates="tools")
    tool = relationship("KitchenTools")

    @property
    def name(self):
        return self.tool.name    
    
  
class RecipeIngredients(Base):
    __tablename__ = "recipe_ingredients"
    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
    quantity = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    component = Column(String, nullable=True)

    recipe = relationship("Recipes", back_populates="ingredients")
    ingredient = relationship("Ingredients")

    @property
    def name(self):
        return self.ingredient.name
    
    
class RecipeCollections(Base):
    __tablename__ = "recipe_collections"
    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), primary_key=True)


    collection = relationship("Collections")
    recipe = relationship("Recipes", back_populates="collections")

    @property
    def name(self):
        return self.collection.name
      

	
