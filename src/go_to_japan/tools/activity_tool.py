from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date



# --- Contexte de planification (préférences & contraintes) ---
class PlanningContext(BaseModel):
    interests: List[str] = Field(default_factory=list, description="Centres d’intérêt à privilégier")
    pace: Literal["lent", "equilibre", "rapide"] = Field(..., description="Rythme souhaité")
    cities_to_exclude: List[str] = Field(default_factory=list, description="Villes à exclure strictement")
    comments: Optional[str] = Field(None, description="Contraintes/notes libres de l’utilisateur")
    services: List[str] = Field(default_factory=list, description='Services/format souhaités liés aux activités (ex. "guided_tour", "workshop")')

# --- Références de source ---
class SourceRef(BaseModel):
    url: HttpUrl = Field(..., description="URL de la source fiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")

# --- Activités principales ---
class Activity(BaseModel):
    timeslot: Literal["morning", "afternoon", "evening"] = Field(..., description="Créneau de la journée")
    name: str = Field(..., description="Nom de l’activité")
    category: str = Field(..., description='Catégorie (ex. "temple", "musée", "jardin", "atelier", "randonnée", "spectacle", "nightlife")')
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$", description='Heure de début "HH:MM" (local)')
    duration_minutes: conint(ge=15, le=480) = Field(..., description="Durée estimée en minutes")
    location_name: str = Field(..., description="Nom du lieu")
    address: str = Field(..., description="Adresse du lieu")
    indoor_outdoor: Literal["indoor", "outdoor", "mixed"] = Field(..., description="Exposition aux conditions météo")
    weather_notes: Optional[str] = Field(None, description="Contraintes météo (pluie, chaleur, etc.)")
    cost_eur: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="Coût estimatif en EUR (TTC)")
    travel_to_next_minutes: Optional[conint(ge=0, le=120)] = Field(None, description="Temps de transition vers la prochaine activité")
    sources: List[SourceRef] = Field(..., min_items=1, description="Sources datées de l’activité")

# --- Alternatives par créneau ---
class AltActivity(BaseModel):
    timeslot: Literal["morning", "afternoon", "evening"] = Field(..., description="Créneau concerné")
    name: str = Field(..., description="Nom de l’alternative")
    category: str = Field(..., description="Catégorie de l’alternative")
    duration_minutes: conint(ge=15, le=480) = Field(..., description="Durée estimée")
    indoor_outdoor: Literal["indoor", "outdoor", "mixed"] = Field(..., description="Exposition aux conditions météo")
    reason: str = Field(..., description='Raison de l’alternative (ex. "pluie", "fermeture exceptionnelle", "surcharge")')
    sources: List[SourceRef] = Field(..., min_items=1, description="Sources datées de l’alternative")

# --- Plan d’un jour ---
class DayPlan(BaseModel):
    city: str = Field(..., description="Ville du jour (NE DOIT PAS être dans cities_to_exclude)")
    date: str = Field(..., description="Date du jour (YYYY-MM-DD)")
    meal_windows: List[str] = Field(default_factory=lambda: ["12:00-14:00", "19:00-21:00"],
                                    description='Fenêtres de repas réservées (ex. "12:00-14:00")')
    activities: List[Activity] = Field(..., min_items=1, description="Activités planifiées du jour")
    alt_options: List[AltActivity] = Field(default_factory=list, description="Alternatives disponibles par créneau")
    assumptions: List[str] = Field(default_factory=list, description="Hypothèses appliquées (ex. rythme → densité)")

# --- Compliance & génération ---
class Compliance(BaseModel):
    exclusions_respected: bool = Field(..., description="True si aucune ville exclue n’est présente")
    notes: Optional[str] = Field(None, description="Détails éventuels sur la conformité")

class GenerationInfo(BaseModel):
    generated_at: str = Field(..., description="Date de génération (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire (ex. "Asia/Tokyo")')

# --- Sortie globale ---
class DailyActivitiesPlan(BaseModel):
    planning_context: PlanningContext = Field(..., description="Préférences et contraintes utilisateur")
    days: List[DayPlan] = Field(..., min_items=1, description="Liste des jours planifiés")
    compliance: Compliance = Field(..., description="Conformité aux exclusions/contraintes")
    generation_info: GenerationInfo = Field(..., description="Métadonnées de génération")

