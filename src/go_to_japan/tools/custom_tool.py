from pydantic import BaseModel, HttpUrl, Field, conint, condecimal
import json
from crewai import Agent, Task, Crew
from typing import List, Union, Type, Optional, Literal
from crewai.tools import BaseTool
from datetime import date


# Modèle de sortie pour le résumé du voyage
class ResumeVoyage(BaseModel):
    nom_voyageur: str
    destination_principale: str
    duree_voyage: str
    budget_estime: str
    type_voyage: str
    resume_complet: str


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
    date_consultation: str = Field(..., description="Date du jour de consultation de la source (YYYY-MM-DD)")

# Prévisions quotidiennes pour une ville (une entrée par jour)
class DailyForecast(BaseModel):
    date: str = Field(..., description="Jour de la prévision (YYYY-MM-DD)")
    weather_summary: WeatherSummary = Field(..., description="Synthèse des conditions météo du jour")
    recommendations: List[Recommendation] = Field(default_factory=list, description="Conseils pratiques strictement météorologiques pour ce jour")

# Modèle par ville : uniquement météo, jour par jour + sources
class CityMeteoInfo(BaseModel):
    daily_forecast: List[DailyForecast] = Field(..., description="Liste des prévisions météorologiques par jour")
    sources: List[Source] = Field(..., description="Sources fiables utilisées pour établir les prévisions de la ville")



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
    generated_at: str = Field(..., description="Date de génération (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire (ex. "Asia/Tokyo")')

# ---- Modèle racine ----

class TransportCityPlan(BaseModel):
    city: str = Field(..., description="Ville concernée")
    segments: List[Segment] = Field(..., min_items=1, description="Segments intra-ville ordonnés")
    passes: List[PassRecommendation] = Field(default_factory=list, description="Pass/titres urbains recommandés")
    assumptions: List[str] = Field(default_factory=list, description="Hypothèses (ex. voyage léger, hors pointe)")
    generation_info: GenerationInfo = Field(..., description="Métadonnées de génération")





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





# --- Références & TOC ---

class SourceRef(BaseModel):
    url: HttpUrl = Field(..., description="URL de la source fiable")
    date: str = Field(..., description="Date de publication/consultation (YYYY-MM-DD)")
    title: Optional[str] = Field(None, description="Titre ou émetteur de la source (optionnel)")

class TocItem(BaseModel):
    level: conint(ge=1, le=6) = Field(..., description="Niveau de titre Markdown (1 à 6)")
    title: str = Field(..., description="Titre affiché")
    anchor: str = Field(..., description="Ancre interne (ex. 'jour-1-kyoto')")

# --- Budget (aperçu) ---

class BudgetOverview(BaseModel):
    total_eur: condecimal(ge=0, max_digits=12, decimal_places=2) = Field(..., description="Total global EUR TTC")
    difference_from_budget_eur: condecimal(max_digits=12, decimal_places=2) = Field(
        ..., description="Total - Budget utilisateur (négatif = sous le budget)"
    )
    status: Literal["under", "over", "on_target"] = Field(..., description="Position vs budget utilisateur")
    by_category: dict[str, condecimal(ge=0, max_digits=12, decimal_places=2)] = Field(
        default_factory=dict, description="Sous-totaux par catégorie (transport, lodging, dining, activities)"
    )

# --- Conformité & génération ---

class ComplianceFlags(BaseModel):
    audit_status: Literal["pass", "attention", "fail"] = Field(..., description="Statut global de l’audit")
    budget_respected: bool = Field(..., description="Budget respecté ou correctement justifié")
    pace_respected: bool = Field(..., description="Rythme {pace} respecté")
    exclusions_respected: bool = Field(..., description="Aucune ville exclue présente")
    sources_dated: bool = Field(..., description="Toutes les sources exigées sont datées")
    units_consistent: bool = Field(..., description="Unités et formats conformes (EUR TTC, minutes, ISO dates)")
    timezone_consistent: bool = Field(..., description="Fuseau horaire cohérent")

class GenerationInfo(BaseModel):
    generated_at: str = Field(..., description="Date de génération (YYYY-MM-DD)")
    timezone: str = Field(..., description='Fuseau horaire (ex. "Asia/Tokyo")')
    audit_report_id: Optional[str] = Field(None, description="Identifiant du rapport d’audit validé")

# --- Métadonnées de contexte (facultatives mais utiles dans l’en-tête) ---

class ItineraryMeta(BaseModel):
    first_name: Optional[str] = Field(None, description="Prénom du voyageur")
    departure_date: Optional[str] = Field(None, description="Date de départ")
    duration_days: Optional[conint(ge=1)] = Field(None, description="Durée en jours")
    cities: List[str] = Field(default_factory=list, description="Villes incluses")
    interests: List[str] = Field(default_factory=list, description="Centres d’intérêt")
    pace: Optional[Literal["lent", "equilibre", "rapide"]] = Field(None, description="Rythme souhaité")
    services: List[str] = Field(default_factory=list, description="Services/format souhaités (ex. visites guidées)")
    cities_to_exclude: List[str] = Field(default_factory=list, description="Villes exclues")
    comments: Optional[str] = Field(None, description="Commentaires/contraintes utilisateur")

# --- Sortie racine de la synthèse ---

class ItinerarySynthesis(BaseModel):
    format: Literal["markdown"] = Field("markdown", description="Format du document de sortie")
    markdown: str = Field(..., description="Contenu Markdown final (FR), prêt à partager")
    toc: List[TocItem] = Field(default_factory=list, description="Table des matières (liens internes)")
    meta: ItineraryMeta = Field(default_factory=ItineraryMeta, description="Métadonnées d’itinéraire")
    budget: Optional[BudgetOverview] = Field(None, description="Aperçu budgétaire consolidé")
    bibliography: List[SourceRef] = Field(default_factory=list, description="Bibliographie des sources datées")
    compliance: ComplianceFlags = Field(..., description="Drapeaux de conformité issus de l’audit")
    generation_info: GenerationInfo = Field(..., description="Métadonnées de génération")




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
