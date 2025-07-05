from pathlib import Path

import joblib
from loguru import logger
import mlflow
from mlflow.client import MlflowClient
from mlflow.models import infer_signature
from pandas import DataFrame, read_csv
from prefect import flow, get_run_logger, task
from sklearn.svm import SVC
import typer

from lap.config import (
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
)

app = typer.Typer()


@task
def search_best_run(experiment_name: str):
    """Searches for the best run in MLflow based on F1 score."""
    logger.info("Searching for best hyperparameters in MLflow...")
    client = MlflowClient()
    runs = client.search_runs(
        experiment_ids=mlflow.get_experiment_by_name(experiment_name).experiment_id,
        filter_string="run_name = 'SVC_Hyperparameter_Optimization'",
        order_by=["metrics.best_cv_f1_score DESC"],
        max_results=1,
    )

    if not runs:
        msg = "No hyperparameter optimization runs found. Please run hp_optim.py first."
        logger.error(msg)
        raise ValueError(msg)

    best_run = runs[0]
    best_params = best_run.data.params
    # Convert string params to their correct types
    best_params['C'] = float(best_params['C'])
    best_params['gamma'] = float(best_params['gamma'])
    logger.success(f"Found best parameters from run {best_run.info.run_id}: {best_params}")
    return best_params, best_run.info.run_id


@task
def load_data(features_path: Path, labels_path: Path) -> tuple[DataFrame, DataFrame]:
    """Loads training data."""
    logger.info("Loading training data...")
    features = read_csv(features_path)
    labels = read_csv(labels_path)
    return features, labels


@task
def train_final_model(
    features: DataFrame,
    labels: DataFrame,
    best_params: dict,
    best_run_id: str,
    model_name: str,
    model_output_path: Path,
):
    """Trains, logs, registers, and saves the final model."""
    with mlflow.start_run(run_name="Final_Model_Training"):
        logger.info("Training final model with best parameters...")
        mlflow.log_params(best_params)
        mlflow.set_tag("source_hp_optim_run_id", best_run_id)

        final_model = SVC(**best_params, random_state=42, probability=True)
        final_model.fit(features, labels.values.ravel())

        # Log and register the model in MLflow
        logger.info("Logging and registering model in MLflow...")
        signature = infer_signature(features, final_model.predict(features))
        model_info = mlflow.sklearn.log_model(
            sk_model=final_model,
            name="model",
            signature=signature,
            registered_model_name=model_name,
        )
        
        logger.success(
            f"Model registered as '{model_name}' "
            f"version {model_info.registered_model_version}."
        )

        # Save the model locally
        logger.info(f"Saving model locally to {model_output_path}...")
        model_output_path.parent.mkdir(exist_ok=True)
        joblib.dump(final_model, model_output_path)
        logger.success("Final model training and saving complete.")


@flow(name="Final Model Training")
def final_training_flow(
    model_name: str = "svc-loan-predictor",
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    model_output_path: Path = MODELS_DIR / "model.joblib",
):
    """Orchestrates the final model training process."""
    logger.remove()
    logger.add(sink=get_run_logger().info, format="{message}")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    best_params, best_run_id = search_best_run(MLFLOW_EXPERIMENT_NAME)
    features, labels = load_data(features_path, labels_path)
    train_final_model(
        features=features,
        labels=labels,
        best_params=best_params,
        best_run_id=best_run_id,
        model_name=model_name,
        model_output_path=model_output_path,
    )


@app.command()
def main(
    model_name: str = "svc-loan-predictor",
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    model_output_path: Path = MODELS_DIR / "model.joblib",
):
    """CLI entrypoint to run the final training flow."""
    final_training_flow(
        model_name=model_name,
        features_path=features_path,
        labels_path=labels_path,
        model_output_path=model_output_path,
    )


if __name__ == "__main__":
    app()
