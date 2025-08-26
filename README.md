# 🌍 Go To Japan AI 

Cette API permet de générer des itinéraires de voyage personnalisés.  
Développée avec *FastAPI*, elle peut être déployée sur un serveur 

---

## 📦 Prérequis

- *Python 3.11+*
- *pip* ou *pipenv*

## Créer l'environement

 
python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows

## Installation des dépendances 


First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
pip install --upgrade pip
pip install -r requirements.txt

### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**


## Lancer l'application 


Se placer dans le repertoire src et lancer 

uvicorn api:gtjia --reload

## Ouvrir dans postman 

http://localhost:8000/kickoff

