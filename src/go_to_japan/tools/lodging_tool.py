from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date



# --- Métadonnées de change (optionnel mais recommandé pour la traçabilité) ---
class FxMeta(BaseModel):
    base: Literal["EUR"] = Field("EUR", description="Devise de base")
    quote: Literal["JPY"] = Field("JPY", description="Devise de conversion")
    rate: condecimal(gt=0, max_digits=12, decimal_places=6) = Field(
        ..., description="Taux EUR→JPY utilisé pour la conversion"
    )
    as_of: str = Field(..., description="Date de référence du taux")
    source_url: Optional[HttpUrl] = Field(None, description="Source du taux de change (optionnel)")

# --- Montants TTC : EUR obligatoire, JPY dérivé ---
class Money(BaseModel):
    eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(
        ..., description="Montant en euros (taxes incluses, devise de base)"
    )
    jpy: Optional[conint(ge=0)] = Field(
        None, description="Montant en yens (taxes incluses), dérivé via le taux EUR→JPY"
    )

# --- Option d'hébergement ---
class AccommodationOption(BaseModel):
    name: str = Field(..., description="Nom de l’hébergement")
    type: Literal["hotel", "ryokan", "guesthouse", "hostel", "aparthotel", "minshuku", "capsule"] = Field(
        ..., description="Catégorie d’hébergement"
    )
    price_per_night: Money = Field(..., description="Prix par nuit TTC (EUR de base, JPY dérivé)")
    total_estimate: Money = Field(..., description="Coût total TTC pour {duration} nuits (EUR de base, JPY dérivé)")
    pros: List[str] = Field(default_factory=list, description="Points forts")
    cons: List[str] = Field(default_factory=list, description="Limites / points faibles")
    link: HttpUrl = Field(..., description="URL de la page source")
    source_date: str = Field(..., description="Date de publication/consultation de la source (YYYY-MM-DD)")

# --- Regroupement par ville ---
class CityAccommodations(BaseModel):
    city: str = Field(..., description="Nom de la ville")
    accommodations: List[AccommodationOption] = Field(
        ..., min_items=2, description="Au moins deux options d’hébergement"
    )

# --- Sortie globale ---
class LodgingOptionsByCity(BaseModel):
    cities: List[CityAccommodations] = Field(
        ..., description="Ensemble des villes et leurs options d’hébergement"
    )
    fx: Optional[FxMeta] = Field(
        None, description="Métadonnées du taux de change utilisé pour calculer les montants JPY"
    )
