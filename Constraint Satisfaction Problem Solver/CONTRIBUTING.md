# Contributing

Contributions are welcome. Here's how to get started: 

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** with clear, commented code
4. **Add tests** if applicable
5. **Commit your changes**: `git commit -m "Add feature: description"`
6. **Push to the branch**: `git push origin feature/your-feature`
7. **Open a Pull Request**

## Development Setup

1. Clone the repository:
   ```bash
   git clone <your-fork-url>
   cd rlfap
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify setup:
   ```bash
   python setup.py
   ```

## Code Style

- Follow PEP 8 Python style guidelines
- Add docstrings to all functions and classes
- Use meaningful variable names
- Comment complex algorithms

## Testing

- Run `make test` to test individual instances
- Run `make demo` to verify basic functionality
- Test new algorithms on multiple instance sizes

## Adding New Algorithms

1. Implement the algorithm in `src/csp.py`
2. Add proper docstrings explaining the algorithm
3. Update `scripts/main.py` to include the new algorithm in benchmarks
4. Add examples to `examples/README.md`

## Bug Reports

Please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Error messages (if any)

## Algorithm Improvements

We welcome:
- New CSP solving algorithms
- Heuristic improvements
- Performance optimizations
- New problem domains

## Questions?

Feel free to open an issue for any questions or discussions!