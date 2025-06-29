from zenml import step
import pandas as pd
import mlflow
import mlflow.pyfunc
from sklearn.metrics import mean_squared_error
import numpy as np
from typing_extensions import Annotated

@step(experiment_tracker="mlflow_tracker")
def evaluate_model(
    ratings_df: pd.DataFrame,
    model_uri: str
) -> Annotated[float, "rmse_score"]:
    """
    Charge le modèle loggé comme artefact.
    """
    print("--- Étape 3 : Évaluation du modèle ---")

    print(f"Chargement du modèle depuis : {model_uri}")
    model = mlflow.pyfunc.load_model(model_uri)  
    print("Modèle chargé avec succès.")

    # Jeu de test simple
    test_df = ratings_df.sample(frac=0.2, random_state=42)
    X_test = test_df[['userId', 'movieId']]
    y_true = test_df['rating']

    y_pred = model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"RMSE calculé : {rmse:.4f}")

    mlflow.log_metric("rmse", rmse)
    print("RMSE logué dans MLflow.")

    return rmse
