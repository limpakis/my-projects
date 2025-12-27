.PHONY: demo test benchmark airline clean install help

# Default target
help:
	@echo "RLFAP CSP Solver - Available Commands:"
	@echo "======================================" 
	@echo "make demo      - Run quick demonstration"
	@echo "make test      - Run test script"
	@echo "make benchmark - Run full benchmark suite"
	@echo "make airline   - Run airline scheduling demo"
	@echo "make install   - Install dependencies"
	@echo "make clean     - Remove cache files"
	@echo "make help      - Show this help message"

# Quick demo
demo:
	python demo.py

# Test individual instance
test:
	python scripts/test_run.py

# Full benchmark suite
benchmark:
	python scripts/main.py

# Airline scheduling
airline:
	python scripts/run_airline.py

# Install dependencies
install:
	pip install -r requirements.txt

# Clean cache files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name ".DS_Store" -delete