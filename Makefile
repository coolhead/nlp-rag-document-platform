SHELL := /bin/bash

PY := python3
VENV := .venv
PIP := $(VENV)/bin/pip
UVICORN := $(VENV)/bin/uvicorn

APP := app.api:app
HOST ?= 0.0.0.0
PORT ?= 8000

DATA_DIR ?= data/raw

.PHONY: help venv install run dev ingest smoke clean

help:
	@echo "Targets:"
	@echo "  make venv        - create venv"
	@echo "  make install     - install deps"
	@echo "  make dev         - run API with reload"
	@echo "  make run         - run API (no reload)"
	@echo "  make ingest      - ingest PDFs from DATA_DIR (default: data/raw)"
	@echo "  make smoke       - quick health check + search call"
	@echo "  make clean       - remove venv + indexes + caches"

venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	@$(PIP) -q install --upgrade pip setuptools wheel
	@echo "✅ venv ready: $(VENV)"

install: venv
	@$(PIP) install -r requirements.txt
	@echo "✅ installed"

dev: install
	@DATA_DIR=data EMBED_MODEL=$${EMBED_MODEL:-sentence-transformers/all-MiniLM-L6-v2} \
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT) --reload

run: install
	@DATA_DIR=data EMBED_MODEL=$${EMBED_MODEL:-sentence-transformers/all-MiniLM-L6-v2} \
	$(UVICORN) $(APP) --host $(HOST) --port $(PORT)

ingest: install
	@echo "📥 Ingesting from: $(DATA_DIR)"
	@curl -sS -X POST "http://localhost:$(PORT)/ingest" \
		-H "Content-Type: application/json" \
		-d "{\"path\":\"$(DATA_DIR)\"}" | python3 -m json.tool

smoke:
	@echo "🧪 Smoke test: /docs and /search"
	@echo "Open: http://localhost:$(PORT)/docs"
	@curl -sS -X POST "http://localhost:$(PORT)/search" \
		-H "Content-Type: application/json" \
		-d '{"query":"what is this document about?","top_k":3}' | python3 -m json.tool

clean:
	@rm -rf $(VENV) __pycache__ .pytest_cache
	@rm -rf data/index
	@find . -name "*.pyc" -delete
	@echo "🧹 cleaned"
