''''
Attention : ici, on se contente de charger les données sans effectuer de nettoyage.
Puisque les données proviennent d'une base de données relationnelle, on suppose qu'elles sont déjà bien structurées et prêtes pour le nettoyage.
Pour consulter les étapes de nettoyage, veuillez vous référer au fichier .ipynb réalisé avant la décision de passer au modèle MLPos sur Google Colab.
Voir le dossier "training model".
'''


# Fichier: steps/ingest_data.py
import pandas as pd
from sqlalchemy import create_engine
from zenml import step
from typing_extensions import Annotated

# --- Configuration de la Base de Données ---
DB_USER = 'root'
DB_PASSWORD = 'rootpassword'
DB_HOST = '127.0.0.1' #'db' # IMPORTANT: On utilise le nom du service docker-compose
DB_PORT = '3306'
DB_NAME = 'movielens'
DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

@step
def ingest_data() -> Annotated[pd.DataFrame, "ratings_df"]:
    """
    Lit les données depuis la base de données MySQL et les retourne en tant que DataFrame.
    """
    print("--- Étape d'ingestion des données ---")
    try:
        engine = create_engine(DATABASE_URI)
        #df = pd.read_sql("SELECT userId, movieId, rating FROM ratings", engine)
        df = pd.read_sql("SELECT userId, movieId, rating FROM ratings ORDER BY RAND() LIMIT 1000", engine)
        print(f"Données chargées avec succès : {len(df)} notes trouvées.")
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture des données depuis la BDD : {e}")
        raise
                