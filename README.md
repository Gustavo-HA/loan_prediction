<h1 align="center">
    <strong>Loan Prediction - Automating Loan Eligibility - MLOps</strong>
</h1>

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

This project serves as the capstone for the [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) by DataTalks.Club. It applies the MLOps principles learned throughout the course to a real-world classification problem.

The task is to predict loan eligibility using a dataset from [Kaggle](https://www.kaggle.com/datasets/altruist/loan-prediction-problem-dataset). Preliminary data analysis, which guided the development process, can be found in the `notebooks/` directory.

## Task Description

### The Challenge
Manually reviewing loan applications is **slow, expensive, and can lead to inconsistent decisions**. The core challenge is to replace this subjective process with a fast, data-driven system to accurately assess an applicant's eligibility in real time.

### The Solution
This project builds a ML classification model to automate the loan eligibility process. Using applicant details like income, credit history, and marital status, the model provides instant recommendations. The goal is to increase efficiency, reduce human bias, and create a scalable system for real-time loan approval.

### MLOps Focus
A successful model requires more than just accurate predictions. This project incorporates **MLOps practices** to ensure the entire system is robust, scalable, and maintainable, making it suitable for a real-world, production environment.


## Tech Stack
* Python
* Terraform: Infrastructure as Code.
* AWS (Kinesis, S3, EC2, ECR, Lambda): Services for development and streaming inference.
* Docker: Containerization
* uv: Dependency management
* Prefect: Workflow orchestration
* MLflow: Experiment tracking & model registry
* ruff: Linter & code formatter
* Evidently: Model monitoring


## Project Organization

```
loan_prediction/    
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks for visualizations and toy tests.
│
├── infrastructure     <- Terraform IaC setup.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         lap (src module) and configuration for tools like black
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── lap   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes lap a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Script to create the processed dataset
    │
    └── modeling                
        ├── __init__.py 
        ├── hp_optim.py         <- Code to make hyperparameter optimization of specific model
        ├── model_selection.py  <- Code to test several models and select the best 
        ├── predict.py          <- Code to run model inference with trained models          
        └── train.py            <- Code to train models
```

--------

