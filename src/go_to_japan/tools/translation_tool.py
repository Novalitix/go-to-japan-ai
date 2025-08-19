from __future__ import annotations

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from go_to_japan.tools.itinerary_synthesis_tool import ItinerarySynthesisJSON


# -- Règles de préservation --
class TranslationPolicy(BaseModel):
    preserve_keys: bool = Field(True, description="Ne pas changer les clés JSON")
    preserve_enums: bool = Field(True, description='Ne pas traduire les valeurs d’énumération (ex. "morning")')
    preserve_formats: List[str] = Field(
        default_factory=lambda: ["YYYY-MM-DD", "HH:MM", "EUR"],
        description="Formats à préserver (dates, heures, devise)"
    )
    preserve_urls: bool = Field(True, description="Ne pas modifier les URLs")
    preserve_numbers: bool = Field(True, description="Ne pas modifier montants et nombres")
    proper_nouns_policy: Literal["preserve", "translate_if_conventional"] = Field(
        "preserve", description="Politique pour les noms propres"
    )

# -- Stats de traduction --
class TranslationStats(BaseModel):
    strings_translated: int = Field(0, description="Chaînes traduites")
    strings_preserved: int = Field(0, description="Chaînes préservées (clés/enums/URLs/nombres)")
    char_count: int = Field(0, description="Volume de caractères traité (approx.)")

# -- Une traduction (par langue) --
class SingleTranslation(BaseModel):
    i18n_labels: Dict[str, str] = Field(
        default_factory=dict,
        description='Libellés UI pour l’affichage (ex. {"morning":"Matin","evening":"Soir"})'
    )
    translated: "ItinerarySynthesisJSON" = Field(
        ..., description="Itinéraire traduit; structure identique à l’entrée"
    )
    stats: TranslationStats = Field(default_factory=TranslationStats, description="Statistiques de traduction")
    warnings: List[str] = Field(default_factory=list, description="Remarques (ex. noms propres non traduits)")

# -- Bloc des 3 langues --
class TranslationsBlock(BaseModel):
    fr: SingleTranslation = Field(..., description="Version française")
    en: SingleTranslation = Field(..., description="Version anglaise")
    ja: SingleTranslation = Field(..., description="Version japonaise")

# -- Sortie trilingue --
class MultilingualItineraryTranslations(BaseModel):
    languages: List[Literal["fr","en","ja"]] = Field(
        default_factory=lambda: ["fr","en","ja"], description="Langues fournies"
    )
    translation_policy: TranslationPolicy = Field(
        default_factory=TranslationPolicy, description="Règles de préservation appliquées"
    )
    translations: TranslationsBlock = Field(..., description="Traductions par langue")
    generated_at: str = Field(..., description='Date du jour de génération "YYYY-MM-DD"')
