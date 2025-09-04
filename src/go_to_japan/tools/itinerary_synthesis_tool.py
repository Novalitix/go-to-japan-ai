

from crewai.tools import BaseTool
from typing import List, Optional, Literal, Dict
from decimal import Decimal
from pydantic import BaseModel, Field, HttpUrl, conint, condecimal

# ---------- SOURCES & MÉTA ----------

class SourceRef(BaseModel):
    url: str = Field(..., description="URL de la source fiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")
    title: Optional[str] = Field(None, description="Titre ou émetteur (optionnel)")

class ItineraryMeta(BaseModel):
    first_name: Optional[str] = Field(None, description="Prénom du voyageur")
    departure_date: str = Field(..., description="Date de départ (YYYY-MM-DD)")
    duration_days: conint(ge=1) = Field(..., description="Durée en jours")
    cities_to_include: List[str] = Field(default_factory=list, description="Villes incluses")
    pace: Literal["lent", "equilibre", "rapide"] = Field(..., description="Rythme souhaité")
    interests: List[str] = Field(default_factory=list, description="Centres d’intérêt")
    services: List[str] = Field(default_factory=list, description="Modules demandés (ex. 'restaurants','lodging')")
    cities_to_exclude: List[str] = Field(default_factory=list, description="Villes exclues")
    comments: Optional[str] = Field(None, description="Contraintes/notes utilisateur")
    budget_eur: Optional[condecimal(ge=0, max_digits=12, decimal_places=2)] = Field(
        None, description="Budget total cible (EUR TTC)"
    )

# ---------- BLOCS VILLE / JOUR ----------

class LodgingOverview(BaseModel):
    name: str = Field(..., description="Nom de l’hébergement")
    link: Optional[str] = Field(None, description="Lien vers la page de l’hébergement")
    address: str = Field(..., description="Adresse complète")
    check_in: Optional[str] = Field(None, description='Heure "HH:MM" si applicable')
    check_out: Optional[str] = Field(None, description='Heure "HH:MM" si applicable')

class PassNote(BaseModel):
    name: str = Field(..., description="Nom du pass")
    link: Optional[str] = Field(None, description="Lien d’information/achat")
    notes: Optional[str] = Field(None, description="Détails utiles (zones, validité, etc.)")

class CityOverview(BaseModel):
    lodging: Optional[LodgingOverview] = Field(None, description="Hébergement principal à la ville")
    transport_notes: Optional[str] = Field(None, description="Notes globales de mobilité")
    passes: List[PassNote] = Field(default_factory=list, description="Pass recommandés pour la ville")

# ---------- JOUR : MÉTÉO / TRANSPORT / ACTIVITÉS / REPAS ----------

class WeatherBrief(BaseModel):
    summary: str = Field(..., description="Synthèse météo du jour")
    temp_avg_c: Optional[condecimal(max_digits=5, decimal_places=1)] = Field(None, description="Température moy. (°C)")
    precip_prob_pct: Optional[conint(ge=0, le=100)] = Field(None, description="Probabilité de précipitations (%)")
    special: Optional[str] = Field(None, description="Phénomènes particuliers")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources météo")

class TransportItem(BaseModel):
    from_: str = Field(..., alias="from", description="Point de départ")
    to: str = Field(..., description="Point d’arrivée")
    mode: Literal["Metro", "JR Urban", "Bus", "Taxi", "Walk", "Ferry", "Shinkansen", "Flight"] = Field(
        ..., description="Mode de transport"
    )
    line_or_service: Optional[str] = Field(None, description='Ligne/service (ex. "Ginza Line")')
    duration_minutes: conint(ge=0) = Field(..., description="Durée estimée (min)")
    cost_eur: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(..., description="Coût EUR TTC")
    reservation_required: bool = Field(..., description="Réservation nécessaire")
    notes: Optional[str] = Field(None, description="Infos utiles (pointe, accessibilité)")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources datées")

class ActivityItem(BaseModel):
    name: str = Field(..., description="Nom de l’activité")
    category: str = Field(..., description="Catégorie (temple, musée, atelier, etc.)")
    start_time: str = Field(..., description='Heure "HH:MM" (local)')
    duration_minutes: conint(ge=15, le=480) = Field(..., description="Durée (min)")
    address: str = Field(..., description="Adresse")
    indoor_outdoor: Literal["indoor", "outdoor", "mixed"] = Field(..., description="Exposition météo")
    weather_notes: Optional[str] = Field(None, description="Dépendances météo")
    cost_eur: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="Coût EUR TTC")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources datées")

class ActivitiesSlots(BaseModel):
    morning: List[ActivityItem] = Field(default_factory=list, description="Activités du matin")
    afternoon: List[ActivityItem] = Field(default_factory=list, description="Activités de l’après-midi")
    evening: List[ActivityItem] = Field(default_factory=list, description="Activités du soir")

class DiningItem(BaseModel):
    restaurant: str = Field(..., description="Nom du restaurant")
    cuisine: str = Field(..., description="Type de cuisine (ramen, izakaya, kaiseki, ...)")
    price_eur: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(..., description="Prix estimatif EUR TTC")
    reservation_needed: bool = Field(..., description="Réservation nécessaire")
    address: str = Field(..., description="Adresse")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources datées")

class DiningSlots(BaseModel):
    breakfast: List[DiningItem] = Field(default_factory=list, description="Options petit déjeuner")
    lunch: List[DiningItem] = Field(default_factory=list, description="Options déjeuner")
    dinner: List[DiningItem] = Field(default_factory=list, description="Options dîner")

class DailyCosts(BaseModel):
    transport: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="EUR TTC")
    activities: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="EUR TTC")
    dining: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="EUR TTC")
    other: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="EUR TTC")
    total: condecimal(ge=0, max_digits=10, decimal_places=2) = Field(0, description="Total jour EUR TTC")

class DayPlan(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD")
    weather: Optional[WeatherBrief] = Field(None, description="Météo du jour")
    transport: List[TransportItem] = Field(default_factory=list, description="Segments pertinents du jour")
    lodging: Optional[LodgingOverview] = Field(None, description="Hébergement (où dormir)")
    activities: ActivitiesSlots = Field(default_factory=ActivitiesSlots, description="Activités par créneau")
    dining: DiningSlots = Field(default_factory=DiningSlots, description="Repas")
    daily_costs_eur: DailyCosts = Field(default_factory=DailyCosts, description="Sous-totaux & total du jour")
    day_sources: List[SourceRef] = Field(default_factory=list, description="Sources additionnelles du jour")

class CityItinerary(BaseModel):
    city: str = Field(..., description="Nom de la ville")
    overview: Optional[CityOverview] = Field(None, description="Aperçu ville (hébergement/passes)")
    days: List[DayPlan] = Field(..., min_items=1, description="Jours de cette ville")

class ItineraryBlock(BaseModel):
    cities: List[CityItinerary] = Field(..., min_items=1, description="Itinéraire groupé par ville")

# ---------- BUDGET / SCÉNARIOS / BIBLIO ----------

class BudgetOverview(BaseModel):
    by_category: Dict[str, condecimal(ge=0, max_digits=12, decimal_places=2)] = Field(
        default_factory=dict, description='Sous-totaux par catégorie (ex. "transport","lodging","dining","activities")'
    )
    total_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Total global EUR TTC")
    difference_from_budget_eur: condecimal(max_digits=12, decimal_places=2) = Field(
        ..., description="Total - Budget utilisateur (négatif = sous le budget)"
    )
    status: Literal["under", "over", "on_target"] = Field(..., description="Position vs budget")

class ScenarioBrief(BaseModel):
    name: str = Field(..., description="Nom du scénario")
    description: str = Field(..., description="Description courte")
    adjustments: List[str] = Field(default_factory=list, description="Ajustements notables (texte)")
    delta_eur: condecimal(max_digits=12, decimal_places=2) = Field(..., description="Δ vs baseline (EUR)")
    new_total_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Nouveau total EUR")
    pros: List[str] = Field(default_factory=list, description="Avantages")
    cons: List[str] = Field(default_factory=list, description="Inconvénients")
    sources: List[SourceRef] = Field(default_factory=list, description="Sources datées")

# ---------- GÉNÉRATION & RACINE ----------

class GenerationInfo(BaseModel):
    generated_at: str = Field(..., description="Date de génération (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire (ex. "Asia/Tokyo")')

class ItinerarySynthesisJSON(BaseModel):
    version: str = Field("1.0", description="Version du schéma")
    meta: ItineraryMeta = Field(..., description="Métadonnées du voyage")
    itinerary: ItineraryBlock = Field(..., description="Itinéraire par ville puis par jour")
    budget_overview: Optional[BudgetOverview] = Field(None, description="Résumé budgétaire")
    scenarios: List[ScenarioBrief] = Field(default_factory=list, description="Scénarios alternatifs")
    bibliography: List[SourceRef] = Field(default_factory=list, description="Bibliographie des sources datées")
    generation_info: GenerationInfo = Field(..., description="Métadonnées de génération")