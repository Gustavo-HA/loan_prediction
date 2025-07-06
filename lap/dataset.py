from pathlib import Path

import typer
from dotenv import load_dotenv
from joblib import dump
from loguru import logger
from pandas import DataFrame, read_csv
from prefect import flow, get_run_logger, task
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
from tqdm import tqdm

from lap.config import (
    INTERIM_DATA_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)

load_dotenv()

app = typer.Typer()


@task(name="clean_data")
def clean_data(
    input_path: Path = RAW_DATA_DIR / "loan_pred.csv",
    output_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
):
    logger.info(f"Reading data from {input_path}")
    df: DataFrame = read_csv(input_path)

    logger.info("Cleaning data...")

    cleaned_df: DataFrame = df.copy()
    cleaned_df.drop(columns=["Loan_ID"], inplace=True)
    cleaned_df["Loan_Status"] = cleaned_df["Loan_Status"].map({"Y": 1, "N": 0})

    # The only problem with the data are null values.
    # Let's impute them.

    col_w_nulls = [
        "Gender",
        "Married",
        "Dependents",
        "Self_Employed",
        "LoanAmount",
        "Loan_Amount_Term",
        "Credit_History",
    ]

    for col in tqdm(col_w_nulls):
        if col in ["LoanAmount"]:
            mean_imputer = SimpleImputer(strategy="mean")
            cleaned_df[col] = mean_imputer.fit_transform(cleaned_df[[col]]).flatten()
        else:
            mf_imputer = SimpleImputer(strategy="most_frequent")
            cleaned_df[col] = mf_imputer.fit_transform(cleaned_df[[col]]).flatten()

    logger.info(f"Writing cleaned data to {output_path}")
    cleaned_df.to_csv(output_path, index=False)
    logger.info("Data cleaning complete.")

    return cleaned_df


@task(name="process_data")
def preproccess_data(
    cleaned_df: DataFrame,
    output_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    logger.info("Processing data...")

    features_df: DataFrame = cleaned_df.drop(columns=["Loan_Status"])
    target_df: DataFrame = cleaned_df[["Loan_Status"]]

    binary_columns = ["Gender", "Married", "Education", "Self_Employed", "Credit_History"]
    cat_columns = ["Property_Area"]
    ord_columns = ["Dependents", "Loan_Amount_Term"]
    num_columns = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount"]

    bin_pipeline = Pipeline(steps=[("encoder", OrdinalEncoder())]).set_output(transform="pandas")

    cat_pipeline = Pipeline(steps=[("encoder", OneHotEncoder(sparse_output=False))]).set_output(
        transform="pandas"
    )

    ord_pipeline = Pipeline(steps=[("encoder", OrdinalEncoder())]).set_output(transform="pandas")

    num_pipeline = Pipeline(steps=[("scaler", StandardScaler())]).set_output(transform="pandas")

    preprocessor = ColumnTransformer(
        transformers=[
            ("binary", bin_pipeline, binary_columns),
            ("categorical", cat_pipeline, cat_columns),
            ("ordinal", ord_pipeline, ord_columns),
            ("numerical", num_pipeline, num_columns),
        ],
        remainder="drop",
    ).set_output(transform="pandas")

    transformed_df = preprocessor.fit_transform(features_df)

    logger.info(f"Writing features to {output_path}")
    transformed_df.to_csv(output_path, index=False)

    logger.info(f"Writing labels to {labels_path}")
    target_df.to_csv(labels_path, index=False)

    logger.info(f"Saving preprocessor to {preprocessor_save_path}")
    dump(preprocessor, preprocessor_save_path)
    logger.info(f"Preprocessor saved to {preprocessor_save_path}")
    logger.info("Data processing complete.")


@flow(name="Data Preprocessing")
def data_preprocessing_flow(
    raw_data_path: Path = RAW_DATA_DIR / "loan_pred.csv",
    cleaned_data_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    """Cleans and preprocesses the data, preparing it for model training."""
    logger.remove()
    logger.add(sink=get_run_logger().info, format="{message}")

    cleaned_df = clean_data(input_path=raw_data_path, output_path=cleaned_data_path)
    preproccess_data(
        cleaned_df=cleaned_df,
        output_path=features_path,
        labels_path=labels_path,
        preprocessor_save_path=preprocessor_save_path,
    )


@app.command()
def main(
    raw_data_path: Path = RAW_DATA_DIR / "loan_pred.csv",
    cleaned_data_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    """Runs the complete data preprocessing pipeline."""
    data_preprocessing_flow(
        raw_data_path=raw_data_path,
        cleaned_data_path=cleaned_data_path,
        features_path=features_path,
        labels_path=labels_path,
        preprocessor_save_path=preprocessor_save_path,
    )


if __name__ == "__main__":
    app()
