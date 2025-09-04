from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date

class Conventions(BaseModel):
    timezone: str = Field("Asia/Tokyo", description="Fuseau horaire de référence")
    currency: Literal["EUR"] = Field("EUR", description="Devise de base")
    units: dict = Field(default_factory=lambda: {"time":"minutes","money":"EUR TTC"}, description="Unités normalisées")
    fx_policy: dict = Field(default_factory=lambda: {"base":"EUR"}, description="Politique de change (si conversion nécessaire)")

class AgentOverview(BaseModel):
    agent: str = Field(..., description="Nom de l’agent (ex. weather_analyst_agent)")
    task: str = Field(..., description="Nom de la tâche (ex. weather_analyst_task)")
    responsibilities: List[str] = Field(..., description="Responsabilités clés de l’agent")
    produces: List[str] = Field(default_factory=list, description="Artefacts produits (noms/logical IDs)")
    consumes: List[str] = Field(default_factory=list, description="Artefacts en entrée attendus")
    success_criteria: List[str] = Field(default_factory=list, description="Critères d’acceptation/succès")

class DataContract(BaseModel):
    artifact: str = Field(..., description="Nom logique de l’artefact (ex. daily_forecast)")
    schema_ref: str = Field(..., description="Référence de schéma ou modèle (ex. CityMeteoInfo)")
    required_fields: List[str] = Field(default_factory=list, description="Champs requis minimaux")
    format_notes: Optional[str] = Field(None, description="Notes de format/validation (ISO dates, etc.)")

class ArtifactSpec(BaseModel):
    artifact: str = Field(..., description="Nom logique de l’artefact")
    owner_agent: str = Field(..., description="Agent responsable/émetteur")
    description: str = Field(..., description="Description courte de l’artefact")

class OrchestrationBootReport(BaseModel):
    conventions: Conventions = Field(..., description="Conventions globales partagées")
    agents_overview: List[AgentOverview] = Field(..., description="Vue d’ensemble des agents")
    data_contracts: List[DataContract] = Field(default_factory=list, description="Contrats de données par artefact")
    artifacts_registry: List[ArtifactSpec] = Field(default_factory=list, description="Registre des artefacts")
    execution_mode: Literal["parallel"] = Field("parallel", description="Mode d’exécution (sans ordre imposé)")
    notes: List[str] = Field(default_factory=list, description="Remarques/hypothèses utiles")
