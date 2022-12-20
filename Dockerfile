FROM python:3.11-alpine AS builder
ENV PYTHONUNBUFFERED 1
RUN mkdir app
WORKDIR  /app
COPY /pyproject.toml /app
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
COPY . .

ENTRYPOINT ["uvicorn", "app.main:app", "--host=0.0.0.0"]
