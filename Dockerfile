
# à utiliser lors de l'étape de dockerisation de tout le code etape final 

# Étape 1: Partir d'une image de base officielle Python
# On utilise une version "slim" pour que notre image finale soit plus légère.
FROM python:3.9-slim

# Étape 2: Définir des variables d'environnement
# Cela empêche Python de créer des fichiers .pyc et de bufferiser les sorties,
# ce qui est une bonne pratique pour les conteneurs.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Étape 3: Définir le répertoire de travail dans le conteneur
WORKDIR /app

# --- NOUVELLE ÉTAPE : Installer les dépendances système nécessaires à la compilation ---
# On met à jour la liste des paquets et on installe les outils de build.
# build-essential contient gcc et d'autres outils vitaux.
RUN apt-get update && apt-get install -y build-essential

# Étape 4: Installer les dépendances
# On copie d'abord SEULEMENT le fichier requirements.txt.
# Docker met en cache chaque étape. Si requirements.txt ne change pas,
# Docker réutilisera le cache pour cette étape, accélérant les builds futurs.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5: Copier tout le reste de notre projet dans le conteneur
# Cela inclut notre dossier 'app', 'models', 'data'.
COPY . .

# Étape 6: Exposer le port
# On indique à Docker que notre application à l'intérieur du conteneur
# écoutera sur le port 8000.
EXPOSE 8000

# Étape 7: Définir la commande à exécuter au démarrage du conteneur
# On utilise uvicorn pour lancer notre application FastAPI.
# --host 0.0.0.0 est crucial pour que l'API soit accessible de l'extérieur du conteneur.
# Le port 8000 doit correspondre au port exposé.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]