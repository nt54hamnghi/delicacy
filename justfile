test:
  poetry run pytest

test-verbose:
  poetry run pytest -vs

test-lastfail:
  poetry run pytest --lf

test-debug:
  poetry run pytest -x --pdb

dev:
  uvicorn delicacy.main:app --reload

build:
  poetry build

cov:
  coverage run --branch -m pytest && coverage report --skip-empty --show-missing
