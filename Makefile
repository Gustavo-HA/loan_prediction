#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = loan_approval_prediction
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python dependencies
.PHONY: requirements
requirements:
	uv sync
	



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Lint using ruff (use `make format` to do formatting)
.PHONY: lint
lint:
	ruff format --check
	ruff check

## Format source code with ruff
.PHONY: format
format:
	ruff check --fix
	ruff format



## Run tests
.PHONY: test
test:
	python -m pytest tests



## Download Data from storage system
.PHONY: sync_data_down
sync_data_down:
	aws s3 sync \
		s3://gus-mlflow-artifacts/loan_prediction/data/ \
		data/ 
	

## Upload Data to storage system
.PHONY: sync_data_up
sync_data_up:
	aws s3 sync \
		data/ \
		s3://gus-mlflow-artifacts/loan_prediction/data/
	



## Set up Python interpreter environment
.PHONY: create_environment
create_environment: requirements
	@echo ">>> New uv virtual environment created. Activate with:"
	@echo ">>> Windows: .\\\\.venv\\\\Scripts\\\\activate"
	@echo ">>> Unix/macOS: source ./.venv/bin/activate"




#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) lap/dataset.py

## Model Selection
.PHONY: model_selection
model_selection: requirements
	$(PYTHON_INTERPRETER) lap/modeling/model_selection.py

## Hyperparameter Optimization
.PHONY: hp_optim
hp_optim: requirements model_selection
	$(PYTHON_INTERPRETER) lap/modeling/hp_optim.py

## Train Final Model
.PHONY: train
train: requirements
	$(PYTHON_INTERPRETER) lap/modeling/train.py

## Run entire pipeline
.PHONY: data_train_pipeline
data_train_pipeline: data model_selection hp_optim train

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
