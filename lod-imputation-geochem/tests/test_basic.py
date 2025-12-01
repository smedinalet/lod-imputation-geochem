"""
Basic tests for LOD imputation methods
"""

import pytest
import pandas as pd
import numpy as np
from lod_imputation import cargar_csv, detectar_lod, aplicar_reemplazo_lod


def test_detectar_lod():
    """Test LOD detection from <value notation"""
    data = {
        'Cu': [10.5, '<5', 20.3, '<5'],
        'Zn': [100, 150, '<50', 200]
    }
    df = pd.DataFrame(data)
    
    df_clean, lod_info = detectar_lod(df)
    
    assert 'Cu' in lod_info
    assert 'Zn' in lod_info
    assert lod_info['Cu'] == 5.0
    assert lod_info['Zn'] == 50.0
    assert df_clean['Cu'].isna().sum() == 2


def test_beta_substitution():
    """Test β-substitution method"""
    data = {
        'Cu': [10.5, np.nan, 20.3, np.nan, 15.2],
        'Zn': [100, 150, np.nan, 200, 180]
    }
    df = pd.DataFrame(data)
    lod_info = {'Cu': 5.0, 'Zn': 50.0}
    
    df_result, log = aplicar_reemplazo_lod(df, lod_info, method='beta')
    
    # Check no NaN remain
    assert df_result.isna().sum().sum() == 0
    
    # Check values are below LOD
    assert (df_result['Cu'] < 5.0).all()


def test_simple_method():
    """Test simple substitution"""
    data = {
        'Cu': [10.5, np.nan, 20.3, np.nan, 15.2]
    }
    df = pd.DataFrame(data)
    lod_info = {'Cu': 5.0}
    
    df_result, log = aplicar_reemplazo_lod(df, lod_info, method='simple')
    
    assert df_result.isna().sum().sum() == 0
    assert log['metodo'].values[0] == 'sqrt2'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])