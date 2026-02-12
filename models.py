from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Master Tables

class KitchenTools(Base):
    __tablename__ = "kitchen_tools"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    given = Column(Boolean, default=False)
    
    recipes = relationship("RecipeTool", back_populates="tool")
    
class Ingredients(Base):
	__tablename__ = "ingredients"
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	
	recipes = relationship("RecipeIngredients", back_populates="ingredient")

# Connection Tables

class RecipeTools(Base):
    __tablename__ = "recipe_tools"
    recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("kitchen_tools.id"), primary_key=True)
    
    recipe = relationship("Recipes", back_populates="tools")
    tool = relationship("KitchenTool")
  
class RecipeIngredients(Base):
	__tablename__ = "recipe_ingredients"
	recipe_id = Column(Integer, ForeignKey("recipes.id"), primary_key=True)
	ingredient_id = Column(Integer, ForeignKey("ingredients.id"), primary_key=True)
	quantity = Column(Float, nullable=True)
	unit = Column(String, nullable=True)
	
	recipe = relationship("Recipes", back_populates="ingredients")
	ingredient = relationship("Ingredients")
	
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
	
	ingredients = relationship("RecipeIngredients", back_populates="recipe")
	tools = relationship("RecipeTools", back_populates="recipe")
	
