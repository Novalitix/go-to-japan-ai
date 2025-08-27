

````md
# 🌍 Go To Japan AI

API pour générer des itinéraires de voyage personnalisés.

---

## 📦 Prérequis

- Python **>=3.10 <3.14**
- `pip` ou `pipenv`

---

## 🔧 Création de l’environnement

```bash
python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows
````

---

## 📥 Installation des dépendances

> Option rapide (si vous utilisez `uv` et le CLI CrewAI)

```bash
pip install uv
crewai install
```

> Option standard

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Variables d’environnement

Créer un fichier `.env` à la racine :

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
MODEL=gpt-4o-mini
SERPER_API_KEY= xxxxxxxxxxxxxxxxxxxxxxxxxx

```

---

## ▶️ Lancer l’application

Depuis le dossier `src` :

```bash
uvicorn api:gtjia --reload
```

Par défaut : [http://localhost:8000](http://localhost:8000)

---

## 🧪 Tester dans Postman ou cURL

**Endpoint :** `POST http://localhost:8000/kickoff`

Exemple `curl` :

```bash
curl -X POST "http://localhost:8000/kickoff" \
  -H "Content-Type: application/json" \
  -d '{
        "planningType": "explore",
        "travelWith": "solo",
        "pace": "equilibre",
        "firstName": "John",
        "departureDate": "2025-10-11",
        "departurePeriod": "",
        "returnDate": "2025-10-13",
        "duration": 2,
        "citiesToInclude": ["Kyoto"],
        "citiesToExclude": [],
        "budget": 5000,
        "comments": "",
        "interests": ["temples"],
        "services": ["restaurants", "lodging"]
      }'
```
