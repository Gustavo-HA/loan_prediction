from prefect import flow

from lap.dataset import data_preprocessing_flow
from lap.modeling.hp_optim import hp_optim_flow
from lap.modeling.train import final_training_flow


@flow(name="Main Pipeline for Processing Data and Retraining Model")
def main():
    """
    The main production pipeline that runs all steps in order:
    1. Data Preprocessing
    2. Hyperparameter Optimization
    3. Final Model Training
    """
    # Call the flows directly. `wait_for` ensures they run in the correct order.
    data_run = data_preprocessing_flow()
    hp_run = hp_optim_flow(wait_for=[data_run])
    final_training_flow(wait_for=[hp_run])


if __name__ == "__main__":
    main()
