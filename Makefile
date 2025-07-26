#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = loan_approval_prediction
PYTHON_VERSION = 3.12
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install requirements
.PHONY: requirements
requirements:
	uv sync

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +


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



## Run unit tests
.PHONY: unit-tests
unit-tests:
	python -m pytest tests

## Run integration tests
.PHONY: integration-tests
integration-tests:
	@if [ -x ./integration-test/run.sh ]; then \
		./integration-test/run.sh; \
	else \
		chmod +x ./integration-test/run.sh && ./integration-test/run.sh; \
	fi

## Run both unit and integration tests
.PHONY: test
test: unit-tests integration-tests

## Set up Python interpreter environment
.PHONY: create_environment
create_environment:
	uv sync
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
data_train_pipeline:
	$(PYTHON_INTERPRETER) lap/main_flow.py

## Instantiate Amazon Services
.PHONY: aws_services
aws_services:
	cd infrastructure && \
	terraform init && \
	terraform plan -var-file=./vars/stg.tfvars && \
	terraform apply -var-file=./vars/stg.tfvars

## Destroy Amazon Services
.PHONY: aws_destroy
aws_destroy:
	cd infrastructure && \
	terraform destroy -var-file=./vars/stg.tfvars

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
