from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date


class SourceRef(BaseModel):
    url: str = Field(..., description="URL de la source fiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")

class Segment(BaseModel):
    from_point: str = Field(..., description='Point de départ (ex. "HND T3", "Hotel", "Tokyo Station Yaesu Exit")')
    to_point: str = Field(..., description='Point d’arrivée')
    mode: Literal["Metro", "JR Urban", "Bus", "Tram", "Taxi", "Walk", "Ferry"] = Field(
        ..., description="Mode de transport")
    operator: Optional[str] = Field(None, description='Opérateur (ex. "Tokyo Metro", "Toei", "JR East")')
    line_or_service: Optional[str] = Field(None, description='Ligne/service (ex. "Ginza Line", "Yamanote")')
    transfers: int = Field(0, ge=0, description="Nombre de correspondances")
    frequency: Optional[str] = Field(None, description='Fréquence si service cadencé (ex. "every 3–5 min")')
    departure_time: Optional[str] = Field(None, description='Heure départ "HH:MM" (local)')
    arrival_time: Optional[str] = Field(None, description='Heure arrivée "HH:MM" (local)')
    duration_minutes: int = Field(..., ge=0, description="Durée estimée en minutes")
    cost_estimate_yen: int = Field(..., ge=0, description="Coût estimé en JPY")
    reservation_required: bool = Field(..., description="Réservation nécessaire")
    notes: Optional[str] = Field(None, description="Contraintes/infos (bagages, accessibilité, pointe, etc.)")
    sources: List[SourceRef] = Field(..., min_items=1, description="Sources datées confirmant l’info")

class PassRecommendation(BaseModel):
    pass_name: str = Field(..., description='Nom du pass (ex. "Tokyo Subway Ticket 48h")')
    coverage: str = Field(..., description="Zones/lignes couvertes")
    validity_days: int = Field(..., ge=1, description="Durée de validité (jours)")
    cost_yen: int = Field(..., ge=0, description="Coût du pass en JPY")
    conditions: str = Field(..., description="Conditions d’éligibilité/usage")
    break_even_explanation: str = Field(..., description="Justification de rentabilité vs tickets à l’unité")
    purchase_options: str = Field(..., description="Où/comment acheter (bornes, guichets, en ligne)")
    sources: List[SourceRef] = Field(..., min_items=1, description="Sources datées pour ce pass")

class GenerationInfo(BaseModel):
    generated_at: str = Field(..., description="Date du jour de génération (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire (ex. "Asia/Tokyo")')

# ---- Modèle racine ----

class TransportCityPlan(BaseModel):
    city: str = Field(..., description="Ville concernée")
    segments: List[Segment] = Field(..., min_items=1, description="Segments intra-ville ordonnés")
    passes: List[PassRecommendation] = Field(default_factory=list, description="Pass/titres urbains recommandés")
    assumptions: List[str] = Field(default_factory=list, description="Hypothèses (ex. voyage léger, hors pointe)")
    generation_info: GenerationInfo = Field(..., description="Métadonnées de génération")
