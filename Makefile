env:
	conda env create -f environment.yaml

update-env:
	conda env update -f environment.yaml -prune

dev:
	pip install -r requirements-dev.txt
	pre-commit install

check:
	black . --check
	isort -rc -c .
	flake8 .

fix:
	seed-isort-config || True
	black .
	isort -rc .

.PHONY: env dev check fix