# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-01

### Added
- **Core imputation methods**:
  - Simple substitution with controlled variance and guaranteed mean
  - β-substitution (Ganser & Hewett, 2010) - optimal for general use
  - Log-Ratio EM (lrEM) algorithm for compositional data
  - Spatial IDW with quadratic weighting function
  
- **Data handling**:
  - Automatic LOD detection from `<value` notation
  - Support for multiple LODs per element
  - Coordinate extraction for spatial methods
  - Comprehensive data validation

- **File management**:
  - Organized output structure (cache, data, output folders)
  - Session-based result storage
  - Detailed logging of all transformations
  - CSV format validation utility

- **Documentation**:
  - Complete README with usage examples
  - Method comparison guide
  - Data format specifications
  - Detailed lrEM algorithm documentation
  - Contributing guidelines

- **Testing and validation**:
  - Test data generation scripts
  - Method comparison utilities
  - CSV validation tool
  - Basic unit tests

### Implementation Notes
- Project developed with assistance from Claude (Anthropic) for:
  - Code architecture and optimization
  - Documentation and best practices
  - Testing strategies
  
- All mathematical methods validated against peer-reviewed literature:
  - Simple method: Standard practice in geochemistry
  - β-substitution: Ganser & Hewett (2010), J. Occup. Environ. Hyg.
  - lrEM: Palarea-Albaladejo & Martín-Fernández (2015), Chemom. Intell. Lab. Syst.
  - IDW: Adapted from geostatistical literature with quadratic enhancement

### Technical Details
- Python 3.8+ compatible
- Dependencies: NumPy, Pandas, SciPy
- Modular architecture for easy extension
- Comprehensive error handling and validation

## [Unreleased]

### Planned Features
- GUI interface for method selection
- Batch processing capabilities
- Additional visualization tools
- Integration with popular geochemistry packages (pyrolite, GeoPyTool)
- Extended documentation with Jupyter notebooks
- More robust error handling for edge cases
- Performance optimizations for large datasets

### Under Consideration
- Additional imputation methods (MLE, Kaplan-Meier)
- Support for right-censored data
- Bayesian approaches for uncertainty quantification
- Export to common geochemistry software formats

---

## Version History

### [0.1.0] - 2024-12-01
First public release with four robust imputation methods.

---

**Notes:**
- For detailed method comparisons, see `docs/METHODS_COMPARISON.md`
- For data format requirements, see `docs/DATA_FORMAT.md`
- For lrEM algorithm details, see `docs/LREM_METHOD.md`