FROM python:3.10-alpine

RUN apk add gcc python3-dev musl-dev linux-headers
RUN pip install uv

WORKDIR /app

ADD fly_dask fly_dask
ADD pyproject.toml pyproject.toml

RUN uv venv
RUN uv pip install -r pyproject.toml
