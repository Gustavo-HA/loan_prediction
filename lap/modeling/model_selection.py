from pathlib import Path
from pandas import DataFrame, read_csv
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)
from prefect import flow, task
import mlflow

from loguru import logger
from tqdm import tqdm
import typer

from lap.config import (
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI
)

app = typer.Typer()


@task(name="train_model",
)
def train_model(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
):
    """This function will train a number of models and log them to MLflow."""
    
    logger.info("Reading features and labels...")
    features: DataFrame = read_csv(features_path)
    labels: DataFrame = read_csv(labels_path)
    
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.2,
        random_state=42
    )
    
    models = {
        "Logistic Regression": LogisticRegression(random_state=42),
        "RandomForest Classifier": RandomForestClassifier(random_state=42),
        "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42)
    }
    
    for model_name, model in models.items():
        with mlflow.start_run(run_name=model_name):
            logger.info(f"Training default {model_name}...")
            
            mlflow.set_tag("model_name", model_name)
            
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            mlflow.log_params(model.get_params())
            
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1_score", f1)
            
            mlflow.sklearn.log_model(model, "model")
            
            logger.success(f"{model_name} trained and logged successfully.")
            

@flow(
    name="Model Training",
)
def training_flow(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    
    train_model(
        features_path=features_path,
        labels_path=labels_path
    )


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
):
    training_flow(
        features_path=features_path,
        labels_path=labels_path
    )


if __name__ == "__main__":
    app()
