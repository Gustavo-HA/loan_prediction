from pathlib import Path

from hyperopt import STATUS_OK, Trials, fmin, hp, space_eval, tpe
from loguru import logger
import mlflow
from pandas import DataFrame, read_csv
from prefect import flow, get_run_logger, task
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.svm import SVC
import typer

from lap.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, PROCESSED_DATA_DIR

app = typer.Typer()


@task(name="hyperparameter_optimization")
def optimize_hyperparameters(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    num_trials: int = 20,
):
    """This function will perform hyperparameter optimization for the SVC model."""

    logger.info("Reading features and labels...")
    features: DataFrame = read_csv(features_path)
    labels: DataFrame = read_csv(labels_path)

    X_train, _, y_train, _ = train_test_split(features, labels, test_size=0.2, random_state=42)

    def objective(params):
        with mlflow.start_run(nested=True):
            mlflow.set_tag("model_name", "SVC")
            mlflow.log_params(params)

            model = SVC(**params, random_state=42)

            score = cross_val_score(
                model, X_train, y_train.values.ravel(), cv=5, scoring="f1_weighted"
            ).mean()

            mlflow.log_metric("f1_weighted_cv_score", score)

            return {"loss": -score, "status": STATUS_OK}

    search_space = {
        "C": hp.loguniform("C", -2, 2),
        "kernel": hp.choice("kernel", ["linear", "rbf", "poly"]),
        "gamma": hp.loguniform("gamma", -2, 2),
    }

    trials = Trials()
    best_params_raw = fmin(
        fn=objective, space=search_space, algo=tpe.suggest, max_evals=num_trials, trials=trials
    )

    best_params = space_eval(search_space, best_params_raw)
    logger.info(f"Best parameters found: {best_params}")

    # Log the best trial information to the parent run
    best_run = sorted(trials.results, key=lambda x: x["loss"])[0]
    mlflow.log_metric("best_cv_f1_score", -best_run["loss"])
    mlflow.log_params(best_params)

    return trials


@flow(name="Hyperparameter Optimization")
def hp_optim_flow(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    num_trials: int = 20,
):
    logger.remove()
    logger.add(sink=get_run_logger().info, format="{message}")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run(run_name="SVC_Hyperparameter_Optimization"):
        optimize_hyperparameters(
            features_path=features_path, labels_path=labels_path, num_trials=num_trials
        )


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    num_trials: int = 20,
):
    """Runs the hyperparameter optimization flow."""
    hp_optim_flow(features_path=features_path, labels_path=labels_path, num_trials=num_trials)


if __name__ == "__main__":
    app()
