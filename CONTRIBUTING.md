# Contributing to Mekaneck

Thank you for your interest in contributing to the Pharmaceutical Maxwell Demon Framework! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Areas for Contribution](#areas-for-contribution)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- **Python 3.8+**
- **Rust 1.75+** (optional, for core implementation)
- **Git**
- **Docker** (optional)

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/mekaneck.git
cd mekaneck

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev

# Or manually:
pip install -r blindhorse/requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests to ensure everything works
make test
```

---

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clean, documented code
- Follow coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
make test

# Run linters
make lint

# Format code
make format

# Run all checks
make check
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add hardware oscillation harvester for GPU frequencies"
```

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(validator): Add GPU frequency harvesting to hardware oscillation validator

Extends hardware oscillation validator to capture GPU clock frequencies
via NVML API. Adds support for NVIDIA, AMD, and Intel GPUs.

Closes #42
```

### 5. Push Changes

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub and create a Pull Request
- Fill out the PR template
- Link related issues
- Request review

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**: `make test`
2. **Run linters**: `make lint`
3. **Format code**: `make format`
4. **Update documentation**: README, docstrings, etc.
5. **Add tests**: For new features or bug fixes
6. **Update CHANGELOG.md**: Describe your changes

### PR Requirements

- **Clear description**: What does this PR do?
- **Tests**: All new code must be tested
- **Documentation**: Update relevant docs
- **No breaking changes**: Unless discussed in issues
- **Single responsibility**: One feature/fix per PR
- **Clean commit history**: Squash if necessary

### Review Process

1. Automated tests run via GitHub Actions
2. At least one maintainer review required
3. Address feedback
4. Once approved, maintainer will merge

---

## Coding Standards

### Python

- **Style**: Follow [PEP 8](https://pep8.org/)
- **Formatting**: Use `black` with line length 120
- **Imports**: Use `isort` with black profile
- **Type hints**: Use type annotations where possible
- **Docstrings**: Use Google-style docstrings

**Example:**

```python
from typing import List, Dict, Tuple

def compute_categorical_distance(coord1: SEntropyCoordinate,
                                 coord2: SEntropyCoordinate) -> float:
    """
    Compute categorical distance in S-entropy space.
    
    Args:
        coord1: First S-entropy coordinate
        coord2: Second S-entropy coordinate
        
    Returns:
        Euclidean distance in categorical space
        
    Example:
        >>> coord1 = SEntropyCoordinate(10.0, 5.0, 2.0, "drug")
        >>> coord2 = SEntropyCoordinate(12.0, 4.0, 3.0, "target")
        >>> distance = compute_categorical_distance(coord1, coord2)
        >>> print(f"Distance: {distance:.2f}")
    """
    ds_k = coord1.s_knowledge - coord2.s_knowledge
    ds_t = coord1.s_time - coord2.s_time
    ds_e = coord1.s_entropy - coord2.s_entropy
    
    return np.sqrt(ds_k**2 + ds_t**2 + ds_e**2)
```

### Rust

- **Style**: Follow Rust standard style (rustfmt)
- **Linting**: Use Clippy
- **Documentation**: Use `///` for doc comments
- **Testing**: Unit tests in same file, integration tests in `tests/`

**Example:**

```rust
/// Computes the harmonic expansion of a base frequency.
///
/// # Arguments
///
/// * `base_freq` - Base frequency in Hz
/// * `n_max` - Maximum harmonic number
///
/// # Returns
///
/// Vector of harmonic frequencies
///
/// # Example
///
/// ```
/// let harmonics = harmonic_expansion(1.0e9, 150);
/// assert_eq!(harmonics.len(), 150);
/// ```
pub fn harmonic_expansion(base_freq: f64, n_max: usize) -> Vec<f64> {
    (1..=n_max)
        .map(|n| (n as f64) * base_freq)
        .collect()
}
```

---

## Testing Guidelines

### Python Tests

- **Framework**: pytest
- **Coverage**: Aim for >80%
- **Location**: `tests/` directory
- **Naming**: `test_*.py` for files, `test_*` for functions

**Example:**

```python
# tests/test_sentropy.py
import pytest
from blindhorse.validators import SEntropyValidator

def test_frequency_to_sentropy_mapping():
    """Test frequency to S-entropy coordinate mapping."""
    validator = SEntropyValidator()
    
    freq = 1e12  # 1 THz
    coord = validator.map_frequency_to_sentropy(freq, "test")
    
    assert coord.frequency_hz == freq
    assert coord.s_knowledge > 0
    assert coord.s_time < 0  # log10(τ) where τ < 1s
    assert coord.s_entropy >= 0

def test_categorical_distance_properties():
    """Test categorical distance satisfies metric properties."""
    validator = SEntropyValidator()
    
    coord1 = validator.map_frequency_to_sentropy(1e12, "A")
    coord2 = validator.map_frequency_to_sentropy(2e12, "B")
    coord3 = validator.map_frequency_to_sentropy(3e12, "C")
    
    # Non-negativity
    d12 = validator.categorical_distance(coord1, coord2)
    assert d12 >= 0
    
    # Triangle inequality
    d13 = validator.categorical_distance(coord1, coord3)
    d23 = validator.categorical_distance(coord2, coord3)
    assert d13 <= d12 + d23
```

### Running Tests

```bash
# All tests
make test

# Specific test file
pytest tests/test_sentropy.py -v

# With coverage
pytest tests/ --cov=blindhorse --cov-report=html
```

---

## Documentation

### Code Documentation

- **Docstrings**: All public functions, classes, and modules
- **Type hints**: Use throughout
- **Examples**: Include usage examples in docstrings
- **Inline comments**: For complex logic only

### README Updates

- Update main `README.md` for new features
- Update `blindhorse/README.md` for validator changes
- Keep examples up-to-date

### Theoretical Documentation

- LaTeX documents in `docs/` and `mekaneck/docs/`
- Follow existing structure
- Include references

---

## Areas for Contribution

### High Priority

1. **Rust Implementation**
   - Port validators to Rust
   - Hardware oscillation harvester
   - Harmonic network builder
   - Performance benchmarks

2. **Experimental Validation**
   - LED spectroscopy data collection
   - EEG/MEG correlation studies
   - Real drug response validation

3. **Performance Optimization**
   - GPU acceleration for network construction
   - Parallel validator execution
   - Memory optimization for large networks

### Medium Priority

4. **Visualization Enhancements**
   - Interactive plots (Plotly/Dash)
   - 3D S-entropy space visualization
   - Real-time monitoring dashboards

5. **Testing & CI**
   - Expand test coverage
   - Property-based testing
   - Performance regression tests

6. **Documentation**
   - Tutorial notebooks
   - Video demonstrations
   - API documentation (Sphinx)

### Low Priority

7. **Tooling**
   - VSCode extension
   - Jupyter widgets
   - Command-line interface

8. **Integration**
   - REST API
   - WebAssembly bindings
   - Cloud deployment

---

## Questions?

- **GitHub Discussions**: Ask questions, share ideas
- **Issues**: Report bugs, request features
- **Email**: kundai@fullscreen-triangle.com

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Mekaneck! 🚀

