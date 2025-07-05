FROM public.ecr.aws/lambda/python:3.12

RUN pip install -U pip
RUN pip install uv

COPY [ "pyproject.toml", "./"]

RUN uv pip install --system .

COPY [ "./deployment/lambda_function.py", "./deployment/model.py", "./" ]

CMD [ "lambda_function.lambda_handler" ]