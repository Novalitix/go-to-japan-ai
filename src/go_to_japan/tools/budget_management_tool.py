from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date



# ---- Références & FX ----

class SourceRef(BaseModel):
    url: HttpUrl = Field(..., description="URL de la source vérifiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")

class FxMeta(BaseModel):
    base: Literal["EUR"] = Field("EUR", description="Devise de base pour l’agrégation")
    quote: Literal["JPY"] = Field("JPY", description="Devise convertie")
    rate: condecimal(gt=0, max_digits=12, decimal_places=6) = Field(..., description="Taux EUR→JPY utilisé")
    as_of: str = Field(..., description="Date du taux")
    source_url: Optional[HttpUrl] = Field(None, description="Source du taux de change")

# ---- Éléments de coût ----

class CostItem(BaseModel):
    label: str = Field(..., description="Nom court de l’élément (ex. 'Tokaido Shinkansen Hikari')")
    category: Literal["transport", "lodging", "dining", "activities"] = Field(..., description="Catégorie budgétaire")
    qty: condecimal(gt=0, max_digits=8, decimal_places=2) = Field(1, description="Quantité (nuits, billets, pers., etc.)")
    unit_cost_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Coût unitaire en EUR TTC")
    total_cost_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Coût total en EUR TTC")
    notes: Optional[str] = Field(None, description="Précisions (taxes incluses, classe, pass applicable, etc.)")
    sources: List[SourceRef] = Field(..., min_items=1, description="Sources datées")

class CategoryBreakdown(BaseModel):
    category: Literal["transport", "lodging", "dining", "activities"] = Field(..., description="Catégorie")
    items: List[CostItem] = Field(..., min_items=1, description="Détails des postes")
    subtotal_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Sous-total en EUR TTC")

# ---- Variantes / Ajustements ----

class Adjustment(BaseModel):
    operation: Literal["add", "remove", "replace", "upgrade", "downgrade"] = Field(..., description="Type d’ajustement")
    target_category: Literal["transport", "lodging", "dining", "activities"] = Field(..., description="Catégorie visée")
    target_label: Optional[str] = Field(None, description="Élément concerné (pour remove/replace)")
    description: str = Field(..., description="Description claire de la modification proposée")
    delta_eur: condecimal(max_digits=12, decimal_places=2) = Field(..., description="Impact sur le budget (négatif = économie)")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources pour l’ajustement (si nouveau prix)")

class Scenario(BaseModel):
    name: str = Field(..., description="Nom court du scénario (ex. 'JR Pass Kansai + Hostel')")
    description: str = Field(..., description="Logique du scénario (ce qui change vs baseline)")
    adjustments: List[Adjustment] = Field(..., min_items=1, description="Liste d’ajustements")
    delta_eur: condecimal(max_digits=12, decimal_places=2) = Field(..., description="Différence totale vs baseline")
    new_total_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Nouveau total EUR")
    pros: List[str] = Field(default_factory=list, description="Avantages")
    cons: List[str] = Field(default_factory=list, description="Inconvénients")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources additionnelles du scénario")

# ---- Résumé & conformité budget ----

class BudgetDelta(BaseModel):
    budget_input_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Budget utilisateur (EUR)")
    difference_from_budget_eur: condecimal(max_digits=12, decimal_places=2) = Field(
        ..., description="Total - Budget (négatif = sous le budget)"
    )
    status: Literal["under", "over", "on_target"] = Field(..., description="Position vs budget")

# ---- Sortie racine ----

class BudgetAggregationOutput(BaseModel):
    breakdown: List[CategoryBreakdown] = Field(..., min_items=1, description="Coûts agrégés par catégorie")
    total_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Total global EUR TTC")
    difference_from_budget: BudgetDelta = Field(..., description="Comparatif vs budget utilisateur")
    scenarios: List[Scenario] = Field(default_factory=list, description="Variantes proposées")
    fx: Optional[FxMeta] = Field(None, description="Métadonnées de change si conversion JPY→EUR utilisée")
    assumptions: List[str] = Field(default_factory=list, description="Hypothèses (ex. 2 voyageurs, 3 nuits, prix TTC)")


