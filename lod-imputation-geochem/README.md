# LOD Imputation Methods for Geochemical Data

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)

A comprehensive Python library for handling left-censored geochemical data (values below the Limit of Detection - LOD). This package implements four robust statistical methods for LOD replacement, designed specifically for compositional data analysis (CoDa) in geochemistry.

## 🎯 Features

- **Four robust imputation methods**:
  - Simple substitution with controlled variance
  - β-substitution (Ganser & Hewett, 2010) - Optimal for general use
  - Log-Ratio EM (lrEM) - State-of-the-art for compositional data
  - Spatial interpolation using Inverse Distance Weighting (IDW)

- **Automatic LOD detection** from `<value` notation
- **Spatial analysis capabilities** for georeferenced samples
- **Comprehensive logging** of all transformations
- **Built for CoDa** - maintains compositional closure

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Methods Overview](#methods-overview)
- [Usage Examples](#usage-examples)
- [Data Format](#data-format)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## 🚀 Installation

### Requirements

- Python 3.8 or higher
- NumPy >= 1.20.0
- Pandas >= 1.3.0
- SciPy >= 1.7.0

### Install from source

```bash
git clone https://github.com/smedinalet/lod-imputation-geochem.git
cd lod-imputation-geochem
pip install -r requirements.txt
```

## 🔥 Quick Start

```python
from lod_imputation import load_data, detect_lod, apply_imputation

# Load your geochemical data
df = load_data('samples.csv')

# Automatically detect LODs from <value notation
df_clean, lod_dict = detect_lod(df)

# Apply β-substitution method (recommended)
df_imputed, log = apply_imputation(
    df_clean, 
    lod_dict, 
    method='beta'
)

# Save results
df_imputed.to_csv('imputed_data.csv', index=False)
```

## 📊 Methods Overview

### 1. Simple Substitution
Conservative approach with guaranteed mean preservation. Replaces LOD values with LOD/√2 with controlled random variation to avoid repeated values.

**Use when**: Quick exploratory analysis, small datasets (n<20)

```python
df_result, log = apply_imputation(df, lod_dict, method='simple')
```

### 2. β-Substitution (Ganser & Hewett, 2010) ⭐ Recommended
Calculates optimal substitution factors from observed data. Produces near-zero bias comparable to Maximum Likelihood Estimation (MLE) but computationally simpler.

**Use when**: You need robust, unbiased estimates (recommended default)

```python
df_result, log = apply_imputation(df, lod_dict, method='beta')
```

**Reference**: Ganser, G.H., & Hewett, P. (2010). An Accurate Substitution Method for Analyzing Censored Data. *Journal of Occupational and Environmental Hygiene*, 7:4, 233-244.

### 3. Log-Ratio EM (lrEM) ⭐ For CoDa
Iterative EM algorithm that imputes missing values using their conditional expectation based on the log-ratio covariance structure. Preserves full compositional properties.

**Use when**: Performing compositional data analysis (state-of-the-art for CoDa)

```python
df_result, log = apply_imputation(
    df, lod_dict, 
    method='lrem', 
    tolerance=0.0001,
    max_iter=50
)
```

**Reference**: Palarea-Albaladejo, J., & Martín-Fernández, J.A. (2015). zCompositions – R package for multivariate imputation of left-censored data. *Chemometrics and Intelligent Laboratory Systems*, 143, 85-96.

### 4. Spatial IDW (Quadratic Model)
Uses spatial context from nearby samples. Implements a quadratic weighting function that considers geological continuity.

**Use when**: Samples are georeferenced and spatial autocorrelation exists

```python
df_result, log = apply_imputation(
    df, lod_dict, 
    method='idw',
    df_coords=coordinates,
    power=2.0
)
```

## 📁 Data Format

Your CSV file should follow this structure:

```csv
Sample_ID,UTM_E,UTM_N,Cu,Zn,Pb,Au
S001,305234.5,6201234.8,45.3,120.5,<5,0.125
S002,305456.2,6201567.3,<10,95.2,8.4,<0.01
S003,305678.9,6201890.1,78.9,<50,12.6,0.089
```

**Key points**:
- Values below LOD: use `<value` notation (e.g., `<5`, `<0.01`)
- Coordinates: optional columns for spatial methods
- Missing data: leave blank or use `null`, `NULL`, `NaN`

See [DATA_FORMAT.md](docs/DATA_FORMAT.md) for detailed specifications.

## 💻 Usage Examples

### Example 1: Basic Workflow

```python
from lod_imputation import load_data, detect_lod, apply_imputation

# Load data
df = load_data('geochemistry.csv')

# Process LODs
df_processed, lod_info = detect_lod(df)

# Separate coordinates from chemical data
df_chem, df_coords = extract_coordinates(df_processed)

# Apply method
df_imputed, log = apply_imputation(df_chem, lod_info, method='beta')

# Examine log
print(log)
# Columns: beta_GM, beta_MEAN, n_censored, percent_censored, etc.
```

### Example 2: Comparing Methods

```python
methods = ['simple', 'beta', 'lrem']
results = {}

for method in methods:
    df_result, log = apply_imputation(df, lod_info, method=method)
    results[method] = df_result

# Compare results for a specific element
element = 'Cu'
comparison = pd.DataFrame({
    method: results[method][element] 
    for method in methods
})
```

### Example 3: Spatial Analysis with IDW

```python
# Requires coordinate columns in your data
df_imputed, log = apply_imputation(
    df_chem, 
    lod_info, 
    method='idw',
    df_coords=df_coords,
    power=2.0,           # IDW exponent
    max_distance=5000,   # Search radius in map units
    min_neighbors=3,     # Minimum valid neighbors
    method_c='div2'      # Conservative approach
)
```

## 📚 API Reference

### Core Functions

#### `load_data(filepath)`
Loads CSV file and performs initial cleaning.

**Parameters**:
- `filepath` (str): Path to CSV file

**Returns**: pandas.DataFrame

#### `detect_lod(df)`
Automatically detects LOD values from `<value` notation.

**Parameters**:
- `df` (DataFrame): Raw data with LOD notation

**Returns**: 
- `df_clean` (DataFrame): Data with LODs as NaN
- `lod_dict` (dict): Dictionary mapping columns to LOD values

#### `apply_imputation(df, lod_dict, method, **kwargs)`
Applies selected imputation method.

**Parameters**:
- `df` (DataFrame): Data with NaN for censored values
- `lod_dict` (dict): LOD information per column
- `method` (str): One of `'simple'`, `'beta'`, `'multiplicative'`, `'idw'`
- `**kwargs`: Method-specific parameters

**Returns**:
- `df_imputed` (DataFrame): Data with imputed values
- `log` (DataFrame): Detailed transformation log

### Method-Specific Parameters

**Simple**:
- `method_simple`: `'sqrt2'` or `'div2'` (default: `'sqrt2'`)

**Beta**:
- No additional parameters

**lrEM**:
- `tolerance` (float): Convergence criterion (default: 0.0001)
- `max_iter` (int): Maximum iterations (default: 50)
- `frac` (float): Fraction for initialization (default: 0.65)
- `ini_method` (str): `'multRepl'` or `'complete_obs'` (default: `'multRepl'`)

**IDW**:
- `df_coords` (DataFrame): Coordinate columns (required)
- `power` (float): Distance decay exponent (default: 2.0)
- `max_distance` (float): Maximum search radius (default: None)
- `min_neighbors` (int): Minimum valid neighbors (default: 3)
- `method_c` (str): `'div2'` or `'sqrt2'` (default: `'div2'`)

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

Generate test data:

```bash
python scripts/01_create_test_data.py
```

Validate your CSV format:

```bash
python scripts/04_validate_csv.py your_data.csv
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📖 Citation

If you use this library in your research, please cite:

```bibtex
@software{lod_imputation_geochem,
  author = {SAMUEL MEDINA LETELIER},
  title = {LOD Imputation Methods for Geochemical Data},
  year = {2025},
  url = {https://github.com/yourusername/lod-imputation-geochem}
}
```

### References

The β-substitution method is based on:

```bibtex
@article{ganser2010accurate,
  title={An accurate substitution method for analyzing censored data},
  author={Ganser, Gary H and Hewett, Paul},
  journal={Journal of Occupational and Environmental Hygiene},
  volume={7},
  number={4},
  pages={233--244},
  year={2010},
  publisher={Taylor \& Francis}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Development assisted by Claude (Anthropic) for code structure and documentation
- β-substitution method based on Ganser & Hewett (2010)
- Inspired by the compositional data analysis community

## 📧 Contact

For questions or suggestions, please open an issue on GitHub or contact [smedinaletelier@gmail.com](mailto:smedinaletelier@gmail.com).

---

**Made with ❤️ for the geochemistry community**