
import os
import pandas as pd
from zenml import step
from surprise import SVD, Reader, Dataset
import mlflow
import mlflow.pyfunc
import joblib
from surprise_wrapper import SurpriseWrapper

from typing_extensions import Annotated

MODEL_FILENAME = "model.joblib"
REGISTERED_MODEL_NAME = "reco-system-svd"

@step(experiment_tracker="mlflow_tracker")
def train_model(ratings_df: pd.DataFrame) -> Annotated[str, "model_uri"]:
    """
    Étape d'entraînement :
    - Entraîne un modèle SVD.
    - Log comme artefact.
    - Enregistre dans le Model Registry.
    - Retourne un URI models:/ pour la suite.
    """
    print("--- Étape 2 : Entraînement et log du modèle PyFunc ---")

    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(ratings_df[['userId', 'movieId', 'rating']], reader)
    trainset = data.build_full_trainset()

    params = {"n_factors": 150, "n_epochs": 25, "lr_all": 0.005, "reg_all": 0.02}
    mlflow.log_params(params)

    algo = SVD(**params, random_state=42)
    algo.fit(trainset)
    print(" Modèle entraîné.")

    # Sauvegarder le modèle Surprise localement
    os.makedirs("surprise_model_files", exist_ok=True)
    model_path = os.path.join("surprise_model_files", MODEL_FILENAME)
    joblib.dump(algo, model_path)
    print(f" Modèle sauvegardé : {model_path}")

    # Log comme artefact PyFunc dans le run actif
    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=SurpriseWrapper(),
        artifacts={"model_path": model_path}
    )

    # Récupérer run_id + artefact_path pour former le runs:/ URI
    run_id = mlflow.active_run().info.run_id
    model_uri_runs = f"runs:/{run_id}/model"
    print(f" Modèle loggé comme artefact à : {model_uri_runs}")

    #  Maintenant on enregistre dans le Model Registry
    result = mlflow.register_model(
        model_uri=model_uri_runs,
        name=REGISTERED_MODEL_NAME
    )
    print(f" Modèle enregistré dans le Model Registry : {result.name} (version {result.version})")

    # Former l'URI final `models:/` pour la suite
    model_uri = f"models:/{REGISTERED_MODEL_NAME}/latest"
    print(f"URI final pour l'étape suivante : {model_uri}")

    return model_uri
