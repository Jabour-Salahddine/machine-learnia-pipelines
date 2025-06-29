


'''
     juste après la réalisation de modél, avant de faire le piplines on a crrer cette api pour les tests 
   
'''


from fastapi import FastAPI, HTTPException
from surprise.dump import load
import pandas as pd
import os


app = FastAPI(
    title="API de Recommandation de Films",
    description="Une API pour obtenir des recommandations de films basées sur le filtrage collaboratif (SVD) pour les utilisateurs connus, et les films populaires pour les nouveaux utilisateurs.",
    version="2.0.0" # Version mise à jour pour refléter les nouvelles fonctionnalités
)



# Définir les chemins relatifs aux fichiers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'recommendation_model.pkl')
DATA_PATH_MOVIES = os.path.join(BASE_DIR, 'data', 'movie.csv')
DATA_PATH_RATINGS = os.path.join(BASE_DIR, 'data', 'rating.csv')

# Variables globales pour stocker nos données et modèles chargés
algo = None
movies_df = None
ratings_df = None 
known_users = set()
TOP_POPULAR_MOVIES = []

# Utiliser l'événement "startup" de FastAPI pour un chargement propre
@app.on_event("startup")
async def load_ressources():
    global algo, movies_df, ratings_df, known_users, TOP_POPULAR_MOVIES

    # Charger le modèle de recommandation entraîné
    print("Chargement du modèle de recommandation...")
    try:
        _, algo = load(MODEL_PATH)
        print("Modèle chargé avec succès.")
    except FileNotFoundError:
        print(f"ERREUR : Fichier modèle non trouvé à l'emplacement {MODEL_PATH}")

    # Charger les données nécessaires
    print("Chargement des données (movies et ratings)...")
    try:
        movies_df = pd.read_csv(DATA_PATH_MOVIES)
        
        # Optimisation : charger uniquement les colonnes nécessaires
        ratings_cols_needed = ['userId', 'movieId', 'rating']
        ratings_df = pd.read_csv(DATA_PATH_RATINGS, usecols=ratings_cols_needed)

        # Créer un set d'IDs d'utilisateurs connus pour des vérifications rapides
        known_users = set(ratings_df['userId'].unique())
        print("Données chargées avec succès.")
        
        # --- Pré-calculer les recommandations populaires ---
        print("Pré-calcul des recommandations populaires...")
        # Calculer le nombre de notes et la note moyenne par film
        movie_stats = ratings_df.groupby('movieId').agg(
            rating_count=('rating', 'size'),
            avg_rating=('rating', 'mean')
        ).reset_index()

        # Fusionner avec les titres
        movie_stats = pd.merge(movie_stats, movies_df, on='movieId')
        
        # Filtrer pour garder les films avec un nombre significatif de notes (ex: > 50)
        popular_movies = movie_stats[movie_stats['rating_count'] > 50]
        
        # Trier et formater la sortie pour les films populaires
        popular_movies_sorted = popular_movies.sort_values('avg_rating', ascending=False)
        TOP_POPULAR_MOVIES = [
            {
                "movie_id": int(row.movieId), 
                "title": row.title,
                "note_moyenne": round(row.avg_rating, 2)
            }
            for _, row in popular_movies_sorted.head(20).iterrows() # On en garde 20 en stock
        ]
        print("Recommandations populaires prêtes.")

    except FileNotFoundError:
        print(f"ERREUR : Fichiers de données non trouvés.")
    except Exception as e:
        print(f"Une erreur est survenue lors du chargement ou du pré-calcul : {e}")




def get_top_n_recommendations_for_api(user_id: int, n: int = 10):
    all_movie_ids = movies_df['movieId'].unique()
    movies_rated_by_user = ratings_df[ratings_df['userId'] == user_id]['movieId'].unique()
    movies_to_predict_ids = [movie_id for movie_id in all_movie_ids if movie_id not in movies_rated_by_user]
    
    predictions = [algo.predict(uid=user_id, iid=movie_id) for movie_id in movies_to_predict_ids]
    
    predictions.sort(key=lambda x: x.est, reverse=True)
    
    top_n_predictions = predictions[:n]
    
    top_n_recommendations = []
    for pred in top_n_predictions:
        movie_title = movies_df.loc[movies_df['movieId'] == pred.iid, 'title'].iloc[0]
        top_n_recommendations.append({
            "movie_id": int(pred.iid),
            "title": movie_title,
            "predicted_rating": round(pred.est, 2)
        })
    return top_n_recommendations



@app.get("/")
def read_root():
    return {"status": "ok", "message": "Bienvenue sur l'API de Recommandation de Films v2 !"}

@app.get("/recommendations/{user_id}")
def get_recommendations_for_user(user_id: int, n: int = 10):
    """
    Retourne les N meilleures recommandations pour un utilisateur.
    - Si l'utilisateur est connu, retourne des recommandations personnalisées (SVD).
    - Si l'utilisateur est inconnu, retourne les N films les plus populaires.
    """
    print(f"Requête reçue pour l'utilisateur {user_id} avec N={n}")
    
    if algo is None or movies_df is None or not TOP_POPULAR_MOVIES:
        raise HTTPException(status_code=503, detail="Service temporairement indisponible: les ressources ne sont pas chargées.")

    if user_id in known_users:
        print(f"Utilisateur {user_id} connu. Génération de recommandations personnalisées.")
        recommendations = get_top_n_recommendations_for_api(user_id=user_id, n=n)
        return {"user_id": user_id, "type": "personnalisées", "recommendations": recommendations}
    else:
        print(f"Utilisateur {user_id} inconnu. Retour des films populaires.")
        return {"user_id": user_id, "type": "populaires", "recommendations": TOP_POPULAR_MOVIES[:n]}