# Utilise une image Python compatible
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Exposer le port de l'app
EXPOSE 8000

# Commande de lancement
CMD ["uvicorn", "src.api:gtjia", "--host", "0.0.0.0", "--port", "8000"]
