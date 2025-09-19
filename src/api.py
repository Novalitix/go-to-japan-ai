from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import json
import asyncio
import uuid

from go_to_japan.main import run

# Load environment variables from .env file
load_dotenv()

gtjia = FastAPI(title="Go To Japan API", description="API for running the GTJAI crew", version="1.0.0")

def write_root_cause(json_filename: str, directory: str, obj: dict):
    """
    Write the given object to a JSON file inside the specified directory.
    
    - If the directory does not exist, it is created.
    - If the file does not exist, it is created.
    - If the file exists, the object is appended as a new entry in a JSON list.

    Args:
        json_filename (str): Name of the JSON file (e.g., 'result.json').
        directory (str): Path to the directory where the file should be written.
        obj (dict): Dictionary to write.
    """
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, json_filename)

    data = []
    # If file exists, load existing data
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Ensure it's a list, otherwise wrap it
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                # If file is empty or corrupted, reset data
                data = []


    # Ensure the object is a dict for JSON serialization
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except Exception as e:
            print(f"Error: input string could not be parsed as JSON: {e}")
            return
    elif not isinstance(obj, dict):
        if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
            obj = obj.to_dict()
        else:
            obj = vars(obj)

    data.append(obj)

    # Write back to file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Object written to {filepath}")

# Schéma d'entrée (adapte à ton cas d’usage)
class InputsPayload(BaseModel):
    Inputs: Dict[str, Any] = Field(..., descrition="inputs for the GTJAI crew")


# @gtjia.get("/health")
# def health():
#     return {"status": "ok"}

# # POST — envoie un dictionnaire JSON
# @gtjia.post("/kickoff_post")
# def kickoff_post(inputs: str):
#     try:
#         data = json.loads(inputs)  # parse le dict JSON depuis l’URL
#         if not isinstance(data, dict):
#             raise ValueError("`inputs` doit être un objet JSON (dict)")
#         output = run(data)
#         write_root_cause("final_output.json", "./final_outputs", output.raw)
#         return {"status": "success", "data": output.raw}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")
    
# # POST — envoie un dictionnaire JSON
# @gtjia.post("/kickoff_post")
# async def kickoff_post(inputs: str):
#     try:
#         data = json.loads(inputs)  # parse le dict JSON
#         if not isinstance(data, dict):
#             raise ValueError("`inputs` doit être un objet JSON (dict)")

#         # Exécuter les fonctions bloquantes dans un thread
#         output = await asyncio.to_thread(run, data)
#         await asyncio.to_thread(write_root_cause, "final_output.json", "./final_outputs", output.raw)

#         return {"status": "success", "data": output.raw}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")




# # GET — passe le dictionnaire en JSON dans le query param `inputs`
# @gtjia.get("/kickoff_get")
# async def kickoff_get(inputs: str):
#     try:
#         data = json.loads(inputs)  # parse le dict JSON
#         if not isinstance(data, dict):
#             raise ValueError("`inputs` doit être un objet JSON (dict)")

#         output = await asyncio.to_thread(run, data)
#         await asyncio.to_thread(write_root_cause, "final_output.json", "./final_outputs", output.raw)

#         return {"status": "success", "data": output.raw}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")




results = {}

@gtjia.get("/health")
async def health():
    return {"status": "ok"}


def run_job(job_id: str, inputs: str):
    """Exécution bloquante dans un thread."""
    try:
        data = json.loads(inputs)  # parse le dict JSON depuis l’URL
        if not isinstance(data, dict):
            raise ValueError("inputs doit être un objet JSON (dict)")
        output = run(data)
        write_root_cause("final_output.json", "./final_outputs", output.raw)
        results[job_id] = {"status": "done", "data": output.raw}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")
    


@gtjia.post("/kickoff_post")
async def kickoff_post(inputs: str, background_tasks: BackgroundTasks):
    try:
        data = json.loads(inputs)
        if not isinstance(data, dict):
            raise ValueError("`inputs` doit être un objet JSON (dict)")

        job_id = str(uuid.uuid4())
        results[job_id] = {"status": "running"}  # marquer comme en cours

        # lancer en arrière-plan
        background_tasks.add_task(run_job, job_id, data)

        return {"status": "accepted", "job_id": job_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Bad inputs: {e}")


@gtjia.get("/results/{job_id}")
async def get_results(job_id: str):
    if job_id not in results:
        raise HTTPException(status_code=404, detail="Job not found")
    return results[job_id]