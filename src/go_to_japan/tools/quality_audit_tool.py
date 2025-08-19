from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date



# --- Types de base ---

Component = Literal["weather", "transport", "lodging", "activities", "dining", "budget", "sources", "context"]
Severity = Literal["critical", "major", "minor"]
Priority = Literal["high", "medium", "low"]

class Inconsistency(BaseModel):
    id: str = Field(..., description="Identifiant unique de l’anomalie")
    severity: Severity = Field(..., description="Gravité de l’anomalie")
    component: Component = Field(..., description="Composant concerné")
    json_path: str = Field(..., description="Chemin JSON (style JSONPath/JSON Pointer) vers l’élément en cause")
    message: str = Field(..., description="Description claire de l’incohérence")
    evidence: Optional[str] = Field(None, description="Preuve/référence courte (ex. valeurs en conflit)")
    suggestion: str = Field(..., description="Correctif concret à appliquer")
    related_ids: List[str] = Field(default_factory=list, description="Éventuels liens vers d’autres anomalies")

class MissingElement(BaseModel):
    component: Component = Field(..., description="Composant où l’élément manque")
    json_path: str = Field(..., description="Emplacement attendu de l’élément")
    description: str = Field(..., description="Ce qui manque précisément (et pourquoi c’est requis)")
    suggestion: str = Field(..., description="Action proposée pour compléter")

class Recommendation(BaseModel):
    priority: Priority = Field(..., description="Priorité de mise en œuvre")
    action: str = Field(..., description="Action concrète à entreprendre")
    rationale: str = Field(..., description="Pourquoi cette action est pertinente")
    expected_impact_eur: Optional[condecimal(max_digits=12, decimal_places=2)] = Field(
        None, description="Impact budgétaire estimé en EUR (si applicable, signe négatif = économie)"
    )
    fixes_issue_ids: List[str] = Field(default_factory=list, description="IDs d’anomalies corrigées par cette action")

class AuditSummary(BaseModel):
    status: Literal["pass", "attention", "fail"] = Field(..., description="État global de l’audit")
    score_percent: conint(ge=0, le=100) = Field(..., description="Score qualité global (0–100)")
    total_issues: conint(ge=0) = Field(..., description="Nb total d’anomalies")
    critical_count: conint(ge=0) = Field(..., description="Nb d’anomalies critiques")
    major_count: conint(ge=0) = Field(..., description="Nb d’anomalies majeures")
    minor_count: conint(ge=0) = Field(..., description="Nb d’anomalies mineures")

class Metrics(BaseModel):
    days_planned: conint(ge=0) = Field(..., description="Nombre de jours planifiés")
    activities_count: conint(ge=0) = Field(..., description="Nombre total d’activités")
    activities_with_sources: conint(ge=0) = Field(..., description="Activités avec au moins une source datée")
    transport_segments_count: conint(ge=0) = Field(..., description="Nombre de segments de transport")
    transport_with_sources: conint(ge=0) = Field(..., description="Segments de transport sourcés")
    accommodations_count: conint(ge=0) = Field(..., description="Nombre d’options d’hébergement")
    accommodations_with_sources: conint(ge=0) = Field(..., description="Options d’hébergement sourcées")
    meals_count: conint(ge=0) = Field(..., description="Nombre total d’entrées repas")
    meals_with_sources: conint(ge=0) = Field(..., description="Repas sourcés")
    budget_items_count: conint(ge=0) = Field(..., description="Nombre d’items budgétaires")
    budget_items_with_sources: conint(ge=0) = Field(..., description="Items budgétaires sourcés")

class Compliance(BaseModel):
    budget_respected: bool = Field(..., description="Total ≤ budget utilisateur (ou justifié par scénarios)")
    pace_respected: bool = Field(..., description="Densité/durées alignées sur {pace}")
    exclusions_respected: bool = Field(..., description="Aucune ville dans {citiesToExclude}")
    sources_dated: bool = Field(..., description="Toutes les sources exigées ont URL + date")
    units_consistent: bool = Field(..., description="Unités conformes (EUR TTC, minutes, dates ISO)")
    timezone_consistent: bool = Field(..., description="Cohérence du fuseau horaire")

class GenerationInfo(BaseModel):
    generated_at: str = Field(..., description="Date de l’audit (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire de référence (ex. "Asia/Tokyo")')

class QualityAuditOutput(BaseModel):
    audit_summary: AuditSummary = Field(..., description="Synthèse chiffrée et statut")
    inconsistencies: List[Inconsistency] = Field(default_factory=list, description="Anomalies détectées")
    missing_elements: List[MissingElement] = Field(default_factory=list, description="Éléments manquants")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Actions priorisées")
    compliance: Compliance = Field(..., description="Drapeaux de conformité")
    metrics: Metrics = Field(..., description="Statistiques de couverture")
    generation_info: GenerationInfo = Field(..., description="Métadonnées d’audit")


