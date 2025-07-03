from pathlib import Path

from loguru import logger
from tqdm import tqdm
from typer import Typer
from pandas import (
    DataFrame,
    read_csv,
    concat
)
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
from sklearn.compose import ColumnTransformer
from prefect import flow, task
from joblib import dump
from dotenv import load_dotenv
import numpy as np

from lap.config import (
    PROCESSED_DATA_DIR, 
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
    MODELS_DIR,
)

load_dotenv()

app: Typer = Typer()

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
    cleaned_df["Loan_Status"] = cleaned_df["Loan_Status"].map(
        {"Y": 1, "N": 0}
    )
    # The only problem with the data are null values.
    # Let's impute them.
    
    col_w_nulls = ["Gender", "Married", "Dependents",
                   "Self_Employed", "LoanAmount", "Loan_Amount_Term",
                   "Credit_History"]
    
    for col in tqdm(col_w_nulls):
        if col in ["LoanAmount"]:
            mean_imputer = SimpleImputer(strategy="mean")
            cleaned_df[col] = mean_imputer.fit_transform(
                cleaned_df[[col]]
                ).flatten()
        else:
            mf_imputer = SimpleImputer(strategy="most_frequent")
            cleaned_df[col] = mf_imputer.fit_transform(
                cleaned_df[[col]]
                ).flatten()
    
    logger.info(f"Writing cleaned data to {output_path}")
    cleaned_df.to_csv(output_path, index=False)
    logger.info("Data cleaning complete.")

    return cleaned_df
    

@task(name="process_data")
def preproccess_data(
    input_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
    output_path: Path = PROCESSED_DATA_DIR / "processed.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    logger.info(f"Reading cleaned data from {input_path}")
    cleaned_df: DataFrame = read_csv(input_path)

    logger.info("Processing data...")
    
    features_df: DataFrame = cleaned_df.drop(columns=["Loan_Status"])
    target_df: DataFrame = cleaned_df[["Loan_Status"]]
    
    binary_columns = ["Gender", "Married", "Education",
                      "Self_Employed", "Credit_History"]
    cat_columns = ["Property_Area"]
    ord_columns = ["Dependents", "Loan_Amount_Term"]
    num_columns = ["ApplicantIncome", "CoapplicantIncome", "LoanAmount"]
    
    bin_pipeline = Pipeline(steps=[
        ("encoder", OrdinalEncoder())
    ]).set_output(transform="pandas")

    cat_pipeline = Pipeline(steps=[
        ("encoder", OneHotEncoder(sparse_output=False))
    ]).set_output(transform="pandas")

    ord_pipeline = Pipeline(steps=[
        ("encoder", OrdinalEncoder())
    ]).set_output(transform="pandas")

    num_pipeline = Pipeline(steps=[
        ("scaler", StandardScaler())
    ]).set_output(transform="pandas")
    
    preprocessor = ColumnTransformer(
    transformers=[
        ("binary", bin_pipeline, binary_columns),
        ("categorical", cat_pipeline, cat_columns),
        ("ordinal", ord_pipeline, ord_columns),
        ("numerical", num_pipeline, num_columns)
    ],
    remainder="drop"
    ).set_output(transform="pandas")
    
    processed_features: DataFrame = preprocessor.fit_transform(features_df)
    
    processed_data: DataFrame = concat(
        [processed_features, target_df],
        axis=1
    )
    
    logger.info(f"Writing processed data to {output_path}")
    processed_data.to_csv(output_path, index=False)
    logger.info("Data processing complete.")
    
    logger.info(f"Saving preprocessor to {preprocessor_save_path}")
    dump(preprocessor, preprocessor_save_path)
    logger.info("Preprocessor saved successfully.")
    
    return preprocessor


@flow(name="Data Preprocessing Flow")
def data_preprocessing_flow(
    input_path: Path = RAW_DATA_DIR / "loan_pred.csv",
    interim_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
    output_path: Path = PROCESSED_DATA_DIR / "processed.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    clean_data(input_path=input_path,
               output_path=interim_path)
    preproccess_data(input_path=interim_path,
                     output_path=output_path,
                     preprocessor_save_path=preprocessor_save_path)

@app.command()
def main(
    input_path: Path = RAW_DATA_DIR / "loan_pred.csv",
    interim_path: Path = INTERIM_DATA_DIR / "cleaned.csv",
    output_path: Path = PROCESSED_DATA_DIR / "processed.csv",
    preprocessor_save_path: Path = MODELS_DIR / "preprocessor.joblib",
):
    data_preprocessing_flow(
        input_path=input_path,
        interim_path=interim_path,
        output_path=output_path,
        preprocessor_save_path=preprocessor_save_path
    )
    
if __name__ == "__main__":
    app()
