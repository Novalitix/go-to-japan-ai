from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import json

from go_to_japan.main import run

# Load environment variables from .env file
load_dotenv()

gtjia = FastAPI(title="Go To Japan API", description="API for running the GTJAI crew", version="1.0.0")

# Schéma d'entrée (adapte à ton cas d’usage)
class InputsPayload(BaseModel):
    Inputs: Dict[str, Any] = Field(..., descrition="inputs for the GTJAI crew")


@gtjia.get("/health")
def health():
    return {"status": "ok"}

# POST — envoie un dictionnaire JSON
@gtjia.post("/kickoff")
def kickoff_post(payload: InputsPayload):
    try:
        return {"ok": True, "data": run(payload.inputs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET — passe le dictionnaire en JSON dans le query param `inputs`
@gtjia.get("/kickoff")
def kickoff_get(inputs: str):
    try:
        data = json.loads(inputs)  # parse le dict JSON depuis l’URL
        if not isinstance(data, dict):
            raise ValueError("`inputs` doit être un objet JSON (dict)")
        output = run(data)
        return {"ok": True, "data": output["raw"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")


