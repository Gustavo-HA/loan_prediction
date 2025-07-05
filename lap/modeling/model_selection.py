from pathlib import Path

from loguru import logger
import mlflow
from mlflow.client import MlflowClient
from mlflow.models import infer_signature
from pandas import DataFrame, read_csv
from prefect import flow, get_run_logger, task
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from tqdm import tqdm
import typer
from xgboost import XGBClassifier

from lap.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, PROCESSED_DATA_DIR

app = typer.Typer()


def get_metrics(y_true, y_pred, training: bool = True):
    """Calculate and return the evaluation metrics."""
    prefix = "tr_" if training else "test_"
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    return {
        prefix + "accuracy": accuracy,
        prefix + "precision": precision,
        prefix + "recall": recall,
        prefix + "f1": f1,
    }


@task(
    name="train_model",
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
        features, labels, test_size=0.2, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(random_state=42),
        "RandomForest Classifier": RandomForestClassifier(random_state=42),
        "Gradient Boosting Classifier": GradientBoostingClassifier(random_state=42),
        "Support Vector Classifier": SVC(random_state=42),
        "XGBoost Classifier": XGBClassifier(random_state=42),
    }

    for model_name, model in tqdm(models.items(), desc="Training models"):
        with mlflow.start_run(run_name=model_name):
            logger.info(f"Training default {model_name}...")

            mlflow.set_tag("model_name", model_name)

            model.fit(X_train, y_train.values.ravel())

            mlflow.log_params(model.get_params())

            y_tr_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            signature = infer_signature(X_train, y_tr_pred)

            tr_metrics = get_metrics(y_train.values.ravel(), y_tr_pred, training=True)
            test_metrics = get_metrics(y_test.values.ravel(), y_test_pred, training=False)

            # Log both training and test metrics
            for metric, value in tr_metrics.items():
                mlflow.log_metric(metric, value)
            for metric, value in test_metrics.items():
                mlflow.log_metric(metric, value)

            mlflow.sklearn.log_model(sk_model=model, name="model", signature=signature)

            logger.success(f"{model_name} trained and logged successfully.")

    select_best_model()


@task(name="Select Best Model")
def select_best_model():
    """Select the best model based on the logged metrics."""
    logger.info("Selecting the best model based on logged metrics...")

    client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    runs = client.search_runs(
        experiment_ids=mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME).experiment_id,
        filter_string="",
        run_view_type=mlflow.entities.ViewType.ACTIVE_ONLY,
        max_results=1000,
        order_by=["metrics.test_f1 DESC"],
    )

    best_run = runs[0] if runs else None

    if best_run:
        logger.success(
            f"Best model found: {best_run.data.tags['model_name']}"
            + "with test F1 score: {best_run.data.metrics['test_f1']}"
        )
        logger.info(f"Run ID: {best_run.info.run_id}")
    else:
        logger.warning("No runs found.")


@flow(
    name="Model Selection",
)
def training_flow(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
):
    # Configure Loguru to use Prefect's logger
    logger.remove()
    logger.add(sink=get_run_logger().info, format="{message}")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    train_model(features_path=features_path, labels_path=labels_path)


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
):
    training_flow(features_path=features_path, labels_path=labels_path)


if __name__ == "__main__":
    app()
