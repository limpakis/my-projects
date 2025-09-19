# ===============================
# Makefile — Offline Assistant
# ===============================

SHELL := /bin/bash
.ONESHELL:

# ---- Paths / Commands ----
PY        := python3
VENV_DIR  := .venv
PIP       := $(VENV_DIR)/bin/pip
PYTHON    := $(VENV_DIR)/bin/python
UVICORN   := $(VENV_DIR)/bin/uvicorn
HTTP_SRVR := $(PYTHON) -m http.server 5500

APP       := app.server:app
PORT      := 9000

# ---- Models to pull via Ollama ----
MODELS := gemma3:1b 

# ---- Default target ----
.PHONY: help
help:
	@echo "Offline Assistant — Make targets"
	@echo ""
	@echo "  make setup          # create venv & install python deps"
	@echo "  make pull-models    # pull Ollama models ($(MODELS))"
	@echo "  make index          # build/update RAG index from ./docs"
	@echo "  make run            # start FastAPI backend (uvicorn) on :$(PORT)"
	@echo "  make web            # serve ./web via http://localhost:5500"
	@echo "  make health         # ping backend /health"
	@echo "  make models-list    # list local Ollama models"
	@echo "  make clean-db       # remove chroma_db/"
	@echo "  make clean-venv     # remove .venv"
	@echo "  make reinstall      # nuke venv & reinstall"
	@echo ""
	@echo "Usage (first time):"
	@echo "  make setup pull-models index run"
	@echo "  # in another terminal: make web"

# ---- Environment setup ----
$(VENV_DIR):
	$(PY) -m venv $(VENV_DIR)

.PHONY: setup
setup: $(VENV_DIR)
	source .venv/bin/activate
	$(PIP) install --upgrade pip
	# base requirements
	$(PIP) install -r requirements.txt
	# explicit rag deps (some envs need these pinned separately)
	$(PIP) install langchain-ollama langchain-community

# ---- Ollama ----
.PHONY: pull-models
pull-models:
	@for m in $(MODELS); do \
		echo "==> ollama pull $$m"; \
		ollama pull $$m || true; \
	done
# uvicorn app.server:app --port 9000 --reload
.PHONY: models-list
models-list:
	curl -s http://localhost:11434/api/tags | sed 's/,/\n/g' | sed 's/[{}"]//g' | grep -E 'model|name|digest' || true

# ---- RAG index ----
.PHONY: index
index:
	@test -d docs || mkdir -p docs
	$(PYTHON) app/rag_index.py

.PHONY: clean-db
clean-db:
	rm -rf chroma_db

# ---- Run servers ----
.PHONY: run
run:
	$(UVICORN) $(APP) --port $(PORT) --reload

.PHONY: web
web:
	cd web && $(HTTP_SRVR)

.PHONY: health
health:
	curl -s http://localhost:$(PORT)/health | sed 's/,/\n/g' || true

# ---- Maintenance ----
.PHONY: clean-venv
clean-venv:
	rm -rf $(VENV_DIR)

.PHONY: reinstall
reinstall: clean-venv setup
