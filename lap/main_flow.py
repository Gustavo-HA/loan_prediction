from prefect import flow

from lap.dataset import data_preprocessing_flow
from lap.modeling.hp_optim import hp_optim_flow
from lap.modeling.train import final_training_flow


@flow(name="Main Loan Prediction Pipeline")
def main_pipeline_flow():
    """
    The main production pipeline that runs all steps in order:
    1. Data Preprocessing
    2. Hyperparameter Optimization
    3. Final Model Training
    """
    # The `wait_for` parameter ensures Prefect executes these flows in the
    # correct order.
    data_run = data_preprocessing_flow.submit()
    hp_run = hp_optim_flow.submit(wait_for=[data_run])
    final_training_flow.submit(wait_for=[hp_run])


if __name__ == "__main__":
    main_pipeline_flow()
