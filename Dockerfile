FROM python:3.11.2-slim-bullseye as poetry-build

# prevent poetry from create a virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VERSION=1.3.2

# Do not check PyPI for a new version of pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_NO_CACHE_DIR=off

# system setup:
WORKDIR /code

RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock /code/

# install dependencies (exclude dev dep)
RUN poetry install --without dev --no-interaction --no-ansi
# install ImageMagick
RUN apt-get update && apt-get install -y imagemagick

COPY . /code/

EXPOSE 8100
CMD ["uvicorn", "delicacy.main:app", "--host", "0.0.0.0", "--port", "8100"]
