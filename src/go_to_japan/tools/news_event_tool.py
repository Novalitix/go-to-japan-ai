from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date



# Modèle de sortie pour les recherches sur les websites
class NewsEvent(BaseModel):
    title: str = Field(..., description="Titre de l’événement ou de l’actualité")
    description: str = Field(..., description="Résumé clair et concis de l’information")
    category: str = Field(..., description="Type d’information (événement, actualité locale, transport, etc.)")
    date: str = Field(..., description="Date ou période de l’événement (format YYYY-MM-DD ou texte descriptif)")
    source_url: str = Field(..., description="URL de la source officielle ou fiable")
    source_date: str = Field(..., description="Date de publication ou de mise à jour de la source (YYYY-MM-DD)")


class CityNewsEvents(BaseModel):
    city: str = Field(..., description="Nom de la ville")
    events: List[NewsEvent] = Field(..., description="Liste des événements/actualités pour cette ville")


class LiveNewsOutput(BaseModel):
    cities: List[CityNewsEvents] = Field(..., description="Actualités regroupées par ville")

