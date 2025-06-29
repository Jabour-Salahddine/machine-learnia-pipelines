

import mlflow.pyfunc
import joblib

class SurpriseWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Charge le fichier joblib sauvegardé comme artefact
        self.model = joblib.load(context.artifacts["model_path"])

    def predict(self, context, model_input):
        """
        model_input : DataFrame avec colonnes userId et movieId
        """
        predictions = []
        for _, row in model_input.iterrows():
            pred = self.model.predict(row['userId'], row['movieId']).est
            predictions.append(pred)
        return predictions
