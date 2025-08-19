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

