# Makefile for car-project

# Path to virtual environment
VENV = .venv
ACTIVATE = source $(VENV)/bin/activate

# Default target: run the app
run: install
	$(ACTIVATE) && cd car-brand-app && streamlit run app.py

# Install dependencies into venv
install:
	cd car-brand-app && pip install -r requirements.txt 
	
# Create venv if it doesn't exist
venv:
	python3 -m venv $(VENV)
	@echo "Virtual environment created. Run 'make install' to install dependencies."

# Clean cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".streamlit" -exec rm -rf {} +
