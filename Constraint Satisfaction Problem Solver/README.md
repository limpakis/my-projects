# RLFAP CSP Solver

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Implementation of CSP solving algorithms for the Radio Link Frequency Assignment Problem (RLFAP) and related optimization problems.

## About

This project implements several algorithms for solving Constraint Satisfaction Problems:
- Backtracking Search with various heuristics
- Forward Checking (FC) with weighted degree heuristic
- Maintaining Arc Consistency (MAC)
- Conflict-Directed Backjumping (FC-CBJ)
- Min-Conflicts Local Search
- Dom/WDeg Heuristic for variable ordering

### Applications

**Radio Link Frequency Assignment Problem (RLFAP)**
- Assigns frequencies to radio links to minimize interference
- Uses binary constraints with distance requirements
- Tested on standard RLFAP benchmark instances

**Airline Crew Pairing Scheduling**
- Solves the Set Cover problem for crew scheduling
- Minimizes costs while covering all flights

## Features

- Multiple CSP solving algorithms (FC, MAC, CBJ, Min-Conflicts)
- Heuristics: MRV, Dom/WDeg, LCV
- Constraint propagation techniques
- Performance tracking (time, assignments, nodes)
- Modular design for adding new problems

## Quick Start

```bash
git clone https://github.com/yourusername/rlfap-csp-solver.git
cd rlfap-csp-solver
pip install -r requirements.txt
python demo.py
```

## �📋 Requirements

- Python 3.7+
- sortedcontainers

## 🔧 Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify Installation
```bash
python setup.py  # Runs setup verification
make demo        # Quick demonstration
```

## � Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/rlfap-csp-solver.git
cd rlfap-csp-solver

# Install dependencies
pip install -r requirements.txt

# Verify setup and run demo
python setup.py
python demo.py
```

## �🔧 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd rlfap

# Install dependencies
pip install -r requirements.txt

# Verify setup
python setup.py
```

Or use the Makefile:
```bash
make install  # Install dependencies
make demo     # Run quick demo
make help     # Show all available commands
```

## Usage

```bash
python demo.py                # Quick demo
python scripts/main.py        # Run benchmarks
python scripts/test_run.py    # Test individual instances
```

This runs all CSP algorithms on RLFAP benchmark instances and displays:
- Algorithm name
- Execution time
- Number of variable assignments
- Success/failure status

### Running Airline Scheduler

```bash
python scripts/run_airline.py
```

### Testing Individual Instances

```bash
python scripts/test_run.py
```

## Algorithms

**Forward Checking with Dom/WDeg** - Combines constraint propagation with weighted degree variable ordering.

**MAC (Maintaining Arc Consistency)** - Uses AC-3 algorithm for stronger constraint propagation.

**FC-CBJ (Conflict-Directed Backjumping)** - Intelligent backtracking using conflict sets.

**Min-Conflicts** - Local search that repairs conflicts by minimizing constraint violations.

## 📈 Performance

The algorithms are benchmarked on standard RLFAP instances with varying difficulty:
- Small instances (11, 6-w2): Solved in milliseconds
- Medium instances (2-f24, 3-f10): Solved in seconds
- Large instances (14-f27, 8-f11): May require minutes

## 🏗️ Project Structure

```
rlfap/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── demo.py               # Quick demonstration script
├── src/                  # Core source code
│   ├── csp.py            # CSP framework and algorithms
│   ├── rlfap.py          # RLFAP problem implementation
│   ├── rlfap_parser.py   # Parser for RLFAP instance files
│   └── airline_scheduling.py # Airline crew pairing problem
├── scripts/              # Executable scripts
│   ├── main.py           # Main RLFAP solver runner
│   ├── test_run.py       # Test script
│   └── run_airline.py    # Airline scheduler runner
├── data/                 # RLFAP instance files
│   ├── var*.txt         # Variable definitions
│   ├── dom*.txt         # Domain definitions
│   └── ctr*.txt         # Constraint definitions
└── examples/            # Example outputs and usage
```

## 🧪 RLFAP Instance Format

RLFAP instances consist of three files:

1. **var\*.txt**: Variables and their domain references
2. **dom\*.txt**: Domain definitions (available frequency values)
3. **ctr\*.txt**: Binary constraints between variables

Example constraint: `1 2 > 10` means |freq(1) - freq(2)| > 10

## 🎓 Educational Value

This project demonstrates:
- **Algorithm Design**: Implementation of classic AI search algorithms
- **Problem Modeling**: Converting real-world problems into CSP formulation
- **Optimization Techniques**: Heuristics and pruning strategies
- **Software Engineering**: Modular, extensible code architecture
- **Performance Analysis**: Empirical comparison of algorithmic approaches

## 📝 Key Concepts

- **Constraint Satisfaction Problems (CSP)**: Variables, domains, and constraints
- **Backtracking Search**: Systematic exploration of solution space
- **Constraint Propagation**: Reducing search space by inferring impossible values
- **Heuristics**: Intelligent ordering to reduce search complexity
- **NP-Complete Problems**: Understanding computational complexity

## 🔬 Experimental Results

The solver successfully tackles various RLFAP benchmarks:
- **Easy instances**: < 1 second
- **Medium instances**: 1-10 seconds
- **Hard instances**: 10-60 seconds

Performance varies by algorithm, with MAC typically outperforming FC on harder instances, while FC-CBJ excels on instances with many dead ends.

## 👨‍💻 Author

**Sotirios Lympakis**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome. Please open an issue first for major changes.

## Author

Sotirios Lympakis

## License

MIT License - see [LICENSE](LICENSE) file.

## Acknowledgments

- RLFAP benchmark instances from CELAR
- CSP framework based on AIMA textbook
