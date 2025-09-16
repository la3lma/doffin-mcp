
.PHONY: venv install run clean

PY?=python

venv:
	$(PY) -m venv .venv
	. .venv/bin/activate

install:
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && python mcp_doffin.py

clean:
	rm -rf .venv __pycache__ .mypy_cache .pytest_cache
