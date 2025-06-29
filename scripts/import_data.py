

    # util juste au debut pour passer nos fichiers de csv vers sql au niveau de notre conteneur docker

import pandas as pd
from sqlalchemy import create_engine
import os
import time

# --- Configuration de la Base de Données ---
DB_USER = 'root'
DB_PASSWORD ='rootpassword'
DB_HOST = '127.0.0.1' 
DB_PORT = '3306'
DB_NAME = 'movielens'

# Chaîne de connexion SQLAlchemy pour MySQL
# Format: 'mysql+mysqlconnector://user:password@host:port/database'
# DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# --- Chemins vers les fichiers CSV ---
# On part du principe que ce script est exécuté depuis la racine du projet
DATA_PATH_MOVIES = './data/movies.csv'
DATA_PATH_RATINGS = './data/ratings.csv'

def import_data_to_db():
    """
    Lit les fichiers CSV et les importe dans la base de données MySQL.
    """
    print("Tentative de connexion à la base de données...")
    
    # Créer un "moteur" de connexion à la base de données
    try:
        engine = create_engine(DATABASE_URI)
        # Tester la connexion
        with engine.connect() as connection:
            print("Connexion à la base de données réussie !")
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        print("Vérifiez que le conteneur Docker de la base de données est bien en cours d'exécution.")
        return

    # --- Importer movies.csv ---
    try:
        print(f"Lecture du fichier {DATA_PATH_MOVIES}...")
        movies_df = pd.read_csv(DATA_PATH_MOVIES)
        
        print(f"Importation de {len(movies_df)} films dans la table 'movies'...")
       
        movies_df.to_sql('movies', con=engine, if_exists='append', index=False)
        print("Importation des films terminée.")

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {DATA_PATH_MOVIES} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'importation des films : {e}")


    # --- Importer ratings.csv ---
    try:
        print(f"\nLecture du fichier {DATA_PATH_RATINGS}...")
        # Pour les très gros fichiers, on peut lire par morceaux (chunks)
        chunk_size = 50000 # Lire 50 000 lignes à la fois
        start_time = time.time()

        for i, chunk in enumerate(pd.read_csv(DATA_PATH_RATINGS, chunksize=chunk_size)):
            print(f"Importation du morceau (chunk) n°{i+1} des notes...")
            chunk.to_sql('ratings', con=engine, if_exists='append', index=False)
        
        end_time = time.time()
        print("Importation des notes terminée.")
        print(f"Temps total pour l'importation des notes : {end_time - start_time:.2f} secondes")

    except FileNotFoundError:
        print(f"ERREUR: Le fichier {DATA_PATH_RATINGS} n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur est survenue lors de l'importation des notes : {e}")


if __name__ == '__main__':
    # Cette condition assure que le code ne s'exécute que si on lance ce fichier directement
    import_data_to_db()