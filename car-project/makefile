# ==== Makefile for car-project ====
# Works on macOS/Linux. No need to `source` the venv manually.

PY      := python3
VENV    := .venv
PYTHON  := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit

APP     := car-brand-app/app.py
REQ     := car-brand-app/requirements.txt

.PHONY: run install venv reinstall upgrade freeze clean help

# Default: run the app (will auto-create venv & install deps if needed)
run: $(VENV)/.installed
	@echo "→ Starting Streamlit…"
	@$(STREAMLIT) run $(APP)

# Create venv if missing
$(VENV):
	@echo "→ Creating virtualenv at $(VENV)…"
	@$(PY) -m venv $(VENV)

# Install/refresh dependencies when requirements.txt changes or venv is new
$(VENV)/.installed: $(REQ) | $(VENV)
	@echo "→ Installing dependencies…"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQ)
	@touch $(VENV)/.installed

# Manually (re)install deps
install: $(VENV)/.installed

# Nuke venv and reinstall cleanly
reinstall:
	@echo "→ Rebuilding venv from scratch…"
	@rm -rf $(VENV)
	@$(MAKE) run

# Upgrade deps to latest allowed by requirements.txt
upgrade:
	@$(PIP) install --upgrade -r $(REQ)

# Freeze the exact environment (optional)
freeze:
	@$(PIP) freeze > car-brand-app/requirements.lock.txt
	@echo "→ Wrote lockfile to car-brand-app/requirements.lock.txt"

# Clean caches
clean:
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type d -name ".streamlit" -prune -exec rm -rf {} + || true
	@echo "→ Cleaned."

help:
	@echo "Targets:"
	@echo "  make run        # create venv if needed, install deps, start app"
	@echo "  make install    # install deps (idempotent)"
	@echo "  make reinstall  # delete venv, reinstall, then run"
	@echo "  make upgrade    # upgrade deps per requirements.txt"
	@echo "  make freeze     # write exact versions to requirements.lock.txt"
	@echo "  make clean      # remove caches"
