


from zenml import pipeline
from steps.ingest_data import ingest_data 
from steps.train_modell import train_model
from steps.evaluate_model import evaluate_model

@pipeline(enable_cache=False)
def reco_training_pipeline():
    print("--- Lancement du pipeline ---")

    ratings_df = ingest_data()
    model_uri = train_model(ratings_df=ratings_df)
    evaluate_model(ratings_df=ratings_df, model_uri=model_uri)

    print("--- Pipeline terminé ---")


