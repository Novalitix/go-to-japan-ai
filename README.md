


# 🌍 Go To Japan AI

API pour générer des carnets de voyage personnalisés.

---

## Sommaire

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Lancement](#lancement)
5. [Endpoints API](#endpoints-api)
6. [Exemples d'appel](#exemples-dappel)
7. [Exemple d'input](#exemple-dinput)

---

## Prérequis

- Python **>=3.10 <3.14**
- `pip` ou `pipenv`

---

## Installation

### Création de l’environnement virtuel

```bash
python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate      # Windows
```

### Installation des dépendances

**Option rapide (uv + CrewAI)**

```bash
pip install uv
crewai install
```

+**Option standard**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Option pyproject.toml**

Si vous préférez utiliser le fichier `pyproject.toml` :

```bash
# Avec pip (Python >= 23.1)

# Ou avec pip-tools
pip install pip-tools
pip-sync requirements.txt
# Ou pour générer requirements.txt depuis pyproject.toml
pip-compile pyproject.toml
```
---

## Configuration

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
MODEL=gpt-4o-mini
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Lancement

Depuis le dossier `src` :

```bash
uvicorn api:gtjia --reload
```

Par défaut : [http://localhost:8000](http://localhost:8000)

---

## Endpoints API

### `GET /health`
Vérifie que l'API fonctionne.

**Réponse :**
```json
{
  "status": "ok"
}
```

---

### `POST /kickoff_post`
Lance la génération d'un itinéraire en tâche de fond.

**Paramètres :**
- `inputs` (str, JSON encodé) : dictionnaire des paramètres du voyage (voir exemple d'input).

**Réponse immédiate :**
```json
{
  "status": "accepted",
  "job_id": "..."
}
```

---

### `GET /results/{job_id}`
Récupère le résultat d'un job lancé avec `/kickoff_post`.

**Réponse :**
```json
{
  "status": "done",
  "data": { /* résultat de l'itinéraire */ }
}
```
ou si le job est en cours :
```json
{
  "status": "running"
}
```
ou si le job n'existe pas :
```json
{
  "detail": "Job not found"
}
```

---

## Exemples d'appel

### cURL

```bash
curl -X POST "http://localhost:8000/kickoff_post" \
  -H "Content-Type: application/json" \
  -d '{
        "planningType": "explore",
        "travelWith": "solo",
        "pace": "equilibre",
        "firstName": "John",
<<<<<<< HEAD
        "departureDate": "2026-05-11",
        "departurePeriod": "",
        "returnDate": "2026-05-13",
=======
        "departureDate": "2025-10-11",
        "departurePeriod": "",
        "returnDate": "2025-10-13",
>>>>>>> 74cde7feb248de26bff1f5d46b6d107a47c1a253
        "duration": 2,
        "citiesToInclude": ["Kyoto"],
        "citiesToExclude": [],
        "budget": 5000,
        "comments": "",
        "interests": ["temples"],
        "services": ["restaurants", "lodging"]
      }'
```

---

## Exemple d'input

À fournir dans le champ `inputs` pour le endpoint `/kickoff_post` :

```json
{
  "planningType": "explore",
  "travelWith": "solo",
  "pace": "equilibre",
  "firstName": "John",
<<<<<<< HEAD
  "departureDate": "2026-05-11",
  "departurePeriod": "",
  "returnDate": "2026-05-13",
=======
  "departureDate": "2025-10-11",
  "departurePeriod": "",
  "returnDate": "2025-10-13",
>>>>>>> 74cde7feb248de26bff1f5d46b6d107a47c1a253
  "duration": 2,
  "citiesToInclude": ["Kyoto"],
  "citiesToExclude": [],
  "budget": 5000,
  "comments": "",
  "interests": ["temples"],
  "services": ["restaurants", "lodging"]
}
