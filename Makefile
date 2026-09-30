test:
	python -m pytest -q
benchmark:
	python -m agent_eval.cli --agent v1 --output reports/baseline
	python -m agent_eval.cli --agent v2 --output reports/latest --compare reports/baseline.json
run:
	uvicorn agent_eval.api:app --host 127.0.0.1 --port 8000
lint:
	ruff check agent_eval agents tests
