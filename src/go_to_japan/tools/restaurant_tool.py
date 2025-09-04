from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date




class SourceRef(BaseModel):
    url: HttpUrl = Field(..., description="URL de la source fiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")

class PriceRange(BaseModel):
    eur_min: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(..., description="Prix minimum en EUR TTC")
    eur_max: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(..., description="Prix maximum en EUR TTC")

class MealEntry(BaseModel):
    day: str = Field(..., description="Jour du repas (YYYY-MM-DD)")
    meal_type: Literal["petit_dejeuner", "dejeuner", "diner"] = Field(..., description="Type de repas")
    restaurant: str = Field(..., description="Nom du restaurant")
    cuisine: str = Field(..., description="Type/style de cuisine (ex. izakaya, ramen, kaiseki)")
    price_range: PriceRange = Field(..., description="Fourchette de prix en EUR (TTC)")
    dish_recommendation: str = Field(..., description="Plat emblématique recommandé")
    address: str = Field(..., description="Adresse complète")
    reservation_needed: bool = Field(..., description="Réservation nécessaire (True/False)")
    source: SourceRef = Field(..., description="Référence de la source (URL + date)")

class DiningPlan(BaseModel):
    meals: List[MealEntry] = Field(..., min_items=3, description="Liste d’entrées repas (au moins un par type par jour)")

