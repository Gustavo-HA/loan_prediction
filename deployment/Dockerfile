FROM ghcr.io/astral-sh/uv:0.8.4 AS uv

# First, bundle the dependencies into the task root.
FROM public.ecr.aws/lambda/python:3.12 AS builder

# Enable bytecode compilation, to improve cold-start performance.
ENV UV_COMPILE_BYTECODE=1

# Disable installer metadata, to create a deterministic layer.
ENV UV_NO_INSTALLER_METADATA=1

# Enable copy mode to support bind mount caching.
ENV UV_LINK_MODE=copy

RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-emit-workspace --no-dev --no-editable -o requirements.txt && \
    uv pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

FROM public.ecr.aws/lambda/python:3.12

# Copy the runtime dependencies from the builder stage.
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Copy the application code into the Lambda task root.
COPY ./deployment/lambda_function.py ${LAMBDA_TASK_ROOT}/lambda_function.py
COPY ./deployment/model.py ${LAMBDA_TASK_ROOT}/model.py
COPY ./models/preprocessor.pkl ${LAMBDA_TASK_ROOT}/preprocessor.pkl

CMD [ "lambda_function.lambda_handler" ]