
.PHONY: venv install run clean test test-unit test-integration test-e2e test-all coverage

PY?=python

venv:
	$(PY) -m venv .venv
	. .venv/bin/activate

install:
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && pip install -r test_requirements.txt

run:
	. .venv/bin/activate && python mcp_doffin.py

test: test-unit test-integration
	@echo "Unit and integration tests completed"

test-unit:
	. .venv/bin/activate && python -m pytest ../tests/test_unit.py -v

test-integration:
	. .venv/bin/activate && python -m pytest ../tests/test_integration.py -v

test-e2e:
	. .venv/bin/activate && python -m pytest ../tests/test_e2e.py -v -m e2e

test-all: test-unit test-integration test-e2e
	@echo "All tests completed"

coverage:
	. .venv/bin/activate && python -m pytest ../tests/test_unit.py ../tests/test_integration.py --cov=mcp_doffin --cov-report=html --cov-report=term

clean:
	rm -rf .venv __pycache__ .mypy_cache .pytest_cache htmlcov .coverage

