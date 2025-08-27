# Utilise une image Python compatible
FROM python:3.12-slim

# Définit le répertoire de travail
WORKDIR /app

# Empêche Python d’écrire des fichiers .pyc et force le flush stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système utiles (facultatif mais recommandé)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le code de l’application
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "src.api:gtjia", "--host", "0.0.0.0", "--port", "8000"]
