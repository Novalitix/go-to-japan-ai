# Utilise une image Python compatible
FROM python:3.12-slim

# Définit le répertoire de travail
WORKDIR /app

# Empêche Python d’écrire des fichiers .pyc et force le flush stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système utiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# (Optionnel) Installer uv et crewai si nécessaires
RUN pip install uv
RUN crewai install
RUN uv tool install crewai

# Copier le code de l’application
COPY . .

# Exposer le port
EXPOSE 8000

# Définir le dossier de travail pour l’exécution (src/)
WORKDIR /app/src

# Commande de démarrage
CMD ["uvicorn", "api:gtjia", "--reload", "--host", "0.0.0.0", "--port", "8000"]
