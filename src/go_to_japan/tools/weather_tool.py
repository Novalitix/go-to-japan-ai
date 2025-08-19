from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date


# Modèle de sortie pour les informations de météo
# Résumé météo pour un jour donné
class WeatherSummary(BaseModel):
    temperatures_moyennes: str = Field(..., description="Températures moyennes prévues pour la journée")
    precipitations_probables: str = Field(..., description="Niveau/quantité de précipitations probables (ex: mm, %)")
    phenomenes_particuliers: Optional[str] = Field(None, description="Phénomènes météorologiques particuliers (ex: vents forts, neige, canicule)")

# Recommandation d’adaptation strictement liée à la météo
class Recommendation(BaseModel):
    conseil: str = Field(..., description="Conseil pratique météo (vêtements, équipement, activité abritée, plan B)")

# Source générale (fiable) utilisée pour la ville/période
class Source(BaseModel):
    url: str = Field(..., description="URL de la source fiable (agence météo, service national, etc.)")
    date_consultation: str = Field(..., description="Date du jour consultation de la source (YYYY-MM-DD)")

# Prévisions quotidiennes pour une ville (une entrée par jour)
class DailyForecast(BaseModel):
    date: str = Field(..., description="Jour de la prévision (YYYY-MM-DD)")
    weather_summary: WeatherSummary = Field(..., description="Synthèse des conditions météo du jour")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Conseils pratiques strictement météorologiques pour ce jour")

# Modèle par ville : uniquement météo, jour par jour + sources
class CityMeteoInfo(BaseModel):
    daily_forecast: List[DailyForecast] = Field(..., description="Liste des prévisions météorologiques par jour")
    sources: List[Source] = Field(..., description="Sources fiables utilisées pour établir les prévisions de la ville")
