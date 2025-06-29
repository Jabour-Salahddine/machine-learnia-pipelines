# Projet : API de Recommandation de Films

Ce projet a pour objectif de construire et de déployer un système de recommandation de films basé sur le filtrage collaboratif. L'API, construite avec FastAPI, fournit des recommandations personnalisées pour les utilisateurs connus et des recommandations populaires pour les nouveaux utilisateurs.

Ce fichier décrit comment le travail a été lancé. L'objectif initial était de réaliser simplement une API en local, étape par étape, jusqu'à parvenir à un pipeline reproductible et bien structuré.

## Table des Matières
1. [Fonctionnalités](#1-fonctionnalités)
2. [Architecture de l'Application](#2-architecture-de-lapplication)
3. [Installation et Lancement Local](#3-installation-et-lancement-local)
4. [Déploiement avec Docker](#4-déploiement-avec-docker)
5. [Défis Rencontrés et Solutions](#5-défis-rencontrés-et-solutions)
6. [Vision d'un Projet Professionnel](#6-vision-dun-projet-professionnel)

---

## 1. Fonctionnalités

*   **Recommandations Personnalisées :** Utilise un modèle SVD (Factorisation de Matrices) entraîné sur le dataset MovieLens pour prédire les notes des films et recommander les plus pertinents pour un utilisateur donné.

*   **Gestion du "Cold Start" :** Pour les utilisateurs inconnus (qui n'étaient pas dans l'ensemble d'entraînement), l'API retourne une liste des films les plus populaires, calculée en fonction du nombre de notes et de la note moyenne.

*   **API Robuste :** Construite avec FastAPI, offrant une documentation automatique (via Swagger UI) et une validation des types de données.


---

## 2. Architecture 1ere de l'Application

Le projet est structuré pour séparer le code de l'application, les modèles et les données :

/recommendation-api/
|
├── app/
| └── main.py # Logique de l'API FastAPI
|
├── models/
| └── recommendation_model.pkl # Modèle SVD pré-entraîné
|
├── data/
| ├── movies.csv # Données des films
| └── ratings.csv # Données des notes
|
├── .dockerignore # Fichiers à ignorer par Docker, car on a rencontrer le problème que l'image est trop grande
├── Dockerfile # Recette pour construire l'image Docker
└── requirements.txt # Dépendances Python

---


## 3. Installation et Lancement Local

Il est fortement recommandé d'utiliser un environnement virtuel isolé pour éviter les conflits de dépendances.

### 3.1. Création de l'environnement (avec Conda)

1.  **Créez l'environnement :**

    ```bash
    conda create --name reco-api python=3.9 -y
    ```

2.  **Activez l'environnement :**
    
    ```bash
    conda activate reco-api
    ```

3.  **Installez les dépendances :** Le paquet `scikit-surprise` nécessite des outils de compilation. Il est préférable de l'installer via `conda-forge` pour éviter les erreurs de compilation sur Windows.
    
    ```bash
    conda install -c conda-forge scikit-surprise -y
    pip install -r requirements.txt
    ```
    
    *(Assurez-vous que `scikit-surprise` n'est PAS listé dans `requirements.txt` si vous utilisez cette méthode)*

### 3.2. Lancement du serveur

Une fois l'environnement activé et les dépendances installées, lancez le serveur FastAPI : (L'API sera accessible à l'adresse http://127.0.0.1:8000.)
```bash
uvicorn app.main:app --reload

## 🚀 Déploiement avec Docker

La containerisation via Docker permet de rendre l'application portable, reproductible et facilement déployable sur le cloud.

### 🔧 1. Construire l’image Docker

```bash
docker build -t reco-api-image .
```

### ▶️ 2. Lancer le conteneur

Cette commande monte les dossiers de données et de modèles comme volumes afin de garder une image Docker légère et de manipuler facilement les fichiers volumineux.

```bash
docker run --rm -p 8000:8000 -v ./data:/app/data -v ./models:/app/models reco-api-image
```

---

## ⚠️ Défis rencontrés & solutions apportées

Ce projet a soulevé plusieurs défis typiques du passage d’un modèle de Machine Learning vers un environnement de production. Voici un résumé des principaux problèmes et des solutions apportées :

### 🛠️ 1. Compilation de `scikit-surprise` sur Windows

- **Problème** : L’installation échouait à cause de l'absence d'un compilateur C.
- **Solution** : Utilisation d’un environnement Conda et installation du paquet via le canal `conda-forge`, qui fournit une version pré-compilée.

### 🧱 2. Erreur de sérialisation JSON

- **Problème** : L’API retournait une erreur 500 (Internal Server Error) car FastAPI ne savait pas convertir les types `numpy.int64` en JSON.
- **Solution** : Conversion manuelle des types NumPy vers des types Python natifs (`int()`).

### 🧠 3. Problème de consommation mémoire

- **Problème** : Le chargement complet du fichier `ratings.csv` (~700 Mo) dépassait la mémoire disponible dans Docker.
- **Solution** : Chargement optimisé avec `pandas.read_csv(usecols=...)` pour ne lire que les colonnes nécessaires.

### 🐳 4. Taille de l'image Docker trop grande

- **Problème** : Inclusion des dossiers `/data` et `/models` dans l’image, la rendant > 2.8 Go.
- **Solution** :
  - Création d’un fichier `.dockerignore` pour exclure ces répertoires.
  - Utilisation de volumes Docker pour les monter à l’exécution.

---

## 🌐 Vision d’un déploiement professionnel

Pour faire évoluer ce prototype vers un système de production robuste, les étapes suivantes sont recommandées :

### 🗃️ 1. Remplacement des fichiers CSV par une base de données

Utiliser une base managée (ex. : **Azure Database for PostgreSQL**) comme source de vérité pour les films et les notations. L’API interrogerait cette base plutôt que de lire des fichiers locaux, ce qui la rendrait plus performante et scalable.

### 🧱 2. Mise en place d’un pipeline MLOps structuré
Pour garantir la reproductibilité, la traçabilité et la robustesse du cycle de vie des modèles, nous avons conçu et implémenté un pipeline de machine learning modulaire en utilisant :

🧪 ZenML comme orchestrateur principal,

📊 MLflow pour le suivi des expériences (params, métriques, artefacts),

🐳 Docker pour la conteneurisation,

🗄️ MySQL pour stocker les données ainsi que les métadonnées MLflow,

🧼 Jupyter/Colab au début pour les explorations et nettoyages manuels, puis migré vers des scripts standardisés.

Le pipeline se compose de plusieurs étapes bien distinctes :

ingest_data : chargement structuré depuis MySQL,

train_model : entraînement d’un modèle de type SVD (bibliothèque surprise),

evaluate_model : évaluation du modèle logué dans MLflow avec une logique spécifique pour contourner l’incompatibilité native entre surprise et les saveurs MLflow standards.


#### 🧠 Adaptation du modèle surprise.SVD à MLflow
Étant donné que le modèle SVD de surprise n’est pas compatible avec les formats standard supportés par MLflow (sklearn, keras, etc.), nous avons adopté une stratégie alternative :

Sauvegarde manuelle du modèle avec joblib,

Log de ce fichier comme artifact brut dans MLflow,

Récupération et chargement explicite dans les étapes avales via mlflow.artifacts.download_artifacts().


#### 🚦 Résultat : un pipeline reproductible, traçable et prêt à déployer
Grâce à cette architecture :

Chaque exécution du pipeline est versionnée et suivie via MLflow,

L’ensemble du processus peut être rejoué et audité facilement,

Le modèle peut être déployé ultérieurement via MLflow Deployer, ou packagé pour une API de prédiction en ligne (ex : FastAPI).
