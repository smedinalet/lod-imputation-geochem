# Contributing to LOD Imputation Methods

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🌟 Ways to Contribute

- **Report bugs**: Open an issue describing the problem
- **Suggest enhancements**: Propose new features or improvements
- **Submit pull requests**: Fix bugs or implement new features
- **Improve documentation**: Help clarify or expand documentation
- **Share use cases**: Tell us how you're using the library

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Environment details**:
   - Python version
   - Operating system
   - Package versions (`pip list`)

2. **Reproduction steps**:
   - Minimal code example
   - Sample data (if possible)
   - Error messages/traceback

3. **Expected vs actual behavior**

## 💡 Suggesting Enhancements

For feature requests:

1. Check if it's already been suggested (Issues)
2. Describe the use case clearly
3. Explain why this would benefit users
4. Provide examples if possible

## 🔧 Development Setup

1. **Fork and clone**:
```bash
git clone https://github.com/yourusername/lod-imputation-geochem.git
cd lod-imputation-geochem
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **Create feature branch**:
```bash
git checkout -b feature/your-feature-name
```

## 📝 Code Style

This project follows:

- **PEP 8** for Python code style
- **NumPy docstring format** for documentation
- **Type hints** where appropriate

### Code formatting
```bash
# Format code
black lod_imputation/

# Check linting
flake8 lod_imputation/

# Type checking
mypy lod_imputation/
```

## ✅ Testing

Before submitting a PR:

1. **Write tests** for new features
2. **Ensure all tests pass**:
```bash
pytest tests/
```

3. **Check code coverage**:
```bash
pytest --cov=lod_imputation tests/
```

## 📤 Submitting Pull Requests

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Update CHANGELOG.md**
4. **Ensure CI passes**
5. **Write clear commit messages**:
```
   Add beta-substitution method validation
   
   - Implement edge case handling for small samples
   - Add unit tests for n < 5 scenarios
   - Update documentation with warnings
```

6. **Reference issues**: Use `Fixes #123` or `Closes #123`

## 📚 Documentation

- Use **NumPy docstring format**
- Include **examples** in docstrings
- Update **README.md** for major changes
- Add **inline comments** for complex logic

Example docstring:
```python
def apply_imputation(df, lod_dict, method, **kwargs):
    """
    Apply selected LOD imputation method to dataset.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataset with NaN values for censored observations
    lod_dict : dict
        Dictionary mapping column names to LOD values
    method : str
        Imputation method: 'simple', 'beta', 'lrem', 'idw'
    **kwargs
        Method-specific parameters
    
    Returns
    -------
    df_imputed : pd.DataFrame
        Dataset with imputed values
    log : pd.DataFrame
        Transformation log with method details
    
    Examples
    --------
    >>> df_result, log = apply_imputation(df, lod_dict, method='beta')
    >>> print(log['beta_GM'].values)
    [0.587, 0.623, 0.541]
    """
```

## 🏗️ Project Structure
```
lod-imputation-geochem/
├── lod_imputation/          # Main package
│   ├── __init__.py
│   ├── reader.py            # Data loading
│   ├── imputation.py        # Core methods
│   ├── lrem.py              # lrEM algorithm
│   └── utils_output.py      # File management
├── tests/                   # Test suite
│   ├── test_reader.py
│   ├── test_imputation.py
│   └── test_integration.py
├── scripts/                 # Helper scripts
│   ├── 01_crear_datos_prueba.py
│   ├── 02_probar_imputation.py
│   ├── 03_probar_beta_substitution.py
│   └── 04_validar_csv.py
├── docs/                    # Documentation
│   ├── DATA_FORMAT.md
│   ├── LREM_METHOD.md
│   └── METHODS_COMPARISON.md
├── examples/                # Usage examples
│   ├── basic_workflow.py
│   └── compare_methods.py
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── README.md
├── CONTRIBUTING.md
├── LICENSE
└── CHANGELOG.md
```

## 🔬 Adding New Methods

When implementing a new imputation method:

1. Add function to `imputation.py`
2. Follow existing naming convention: `reemplazar_lod_<method_name>`
3. Update `aplicar_reemplazo_lod()` to include new method
4. Write comprehensive tests
5. Document method in README.md
6. Add academic references if applicable

## 🤔 Questions?

Open an issue with the `question` label or contact the maintainers.

## 📜 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards others

## 🎉 Recognition

Contributors will be acknowledged in:
- README.md (Contributors section)
- CHANGELOG.md (for significant contributions)
- GitHub releases

Thank you for contributing to better geochemical data analysis! 🌍