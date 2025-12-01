# Data Format Guide - LOD Imputation Library

## 📋 Required Format: CSV

Your data file must be a **CSV (Comma-Separated Values)** file with the following characteristics:

---

## 📊 Basic Structure

### **Example of correct geochemical data:**
```csv
Sample_ID,UTM_E,UTM_N,Cu,Zn,Pb,Au,Ag
S001,305234.5,6201234.8,45.3,120.5,<5,0.125,<0.5
S002,305456.2,6201567.3,<10,95.2,8.4,<0.01,0.8
S003,305678.9,6201890.1,78.9,<50,12.6,0.089,1.2
S004,305901.6,6202213.5,123.4,180.3,<5,<0.01,<0.5
S005,306124.3,6202536.9,<10,210.7,15.8,0.234,2.1
```

---

## ✅ REQUIRED Components

### **1. Header Row (Column Names)**
```csv
Sample_ID,UTM_E,UTM_N,Cu,Zn,Pb,Au
```

**Characteristics:**
- ✅ First line of file
- ✅ No extra spaces (will be stripped automatically)
- ✅ Descriptive names
- ⚠️ Avoid special characters (á, é, ñ, etc.)
- ⚠️ Avoid spaces in column names (use underscore: `Sample_ID` not `Sample ID`)

---

### **2. Identification Columns (optional but recommended)**
```csv
Sample_ID,Campaign,Date,Lab_ID,...
S001,Summer2024,2024-01-15,LAB-A,...
```

**Useful for:**
- Tracking specific samples
- Subsequent analyses
- Identifying outliers
- Quality control

---

### **3. Coordinate Columns (required for IDW method)**
```csv
UTM_E,UTM_N,Cu,Zn
305234.5,6201234.8,45.3,120.5
```

**Accepted column names:**
- `UTM_E`, `UTM_N`
- `EASTING`, `NORTHING`
- `X`, `Y`
- Any pair of numeric columns

**The system automatically detects them if they contain:**
- "UTM" in the name
- "EASTING" or "NORTHING"

**Coordinate systems supported:**
- UTM (Universal Transverse Mercator)
- Local grid coordinates
- Any projected coordinate system (not lat/lon)

---

### **4. Geochemical Data Columns (core of analysis)**
```csv
Cu,Zn,Pb,Au,Ag,As,Mo
45.3,120.5,8.2,0.125,1.2,<5,<2
```

**Accepted value formats:**

#### ✅ **Detected values (normal):**
```
45.3
120.5
0.125
1500
0.001
```

#### ✅ **Values below LOD (limit of detection):**
```
<5         (recommended)
<0.01      (recommended)
< 5        (with space, also works)
<10.5
< 0.001
```

#### ✅ **Null/missing values:**
```
null
NULL
NaN
(empty cell)
```

**⚠️ IMPORTANT:** The system automatically converts:
- `"null"`, `"NULL"`, `"NaN"`, `""` → `NaN` (missing value)
- `"<5"`, `"<0.01"` → `NaN` (and saves LOD=5 or 0.01)

---

## 📐 Complete Examples

### **Example 1: Basic data without coordinates**
```csv
Sample,Cu,Zn,Pb,Au
S001,45.3,<10,8.2,0.125
S002,<5,95.2,<3,<0.01
S003,78.9,120.5,12.6,0.089
S004,123.4,<10,<3,0.156
S005,<5,210.7,15.8,<0.01
```

**Methods available:** Simple, β-substitution, lrEM
**Methods NOT available:** IDW (requires coordinates)

---

### **Example 2: Complete data with coordinates**
```csv
Sample_ID,UTM_E,UTM_N,Cu,Zn,Pb,Au,Ag,Mo
S001,305234.5,6201234.8,45.3,120.5,<5,0.125,<0.5,<2
S002,305456.2,6201567.3,<10,95.2,8.4,<0.01,0.8,3.2
S003,305678.9,6201890.1,78.9,<50,12.6,0.089,1.2,<2
S004,305901.6,6202213.5,123.4,180.3,<5,<0.01,<0.5,5.1
S005,306124.3,6202536.9,<10,210.7,15.8,0.234,2.1,<2
S006,306347.0,6202860.3,156.7,<50,<5,0.156,<0.5,4.8
```

**Methods available:** ALL (Simple, β-substitution, lrEM, IDW)

---

### **Example 3: Data with multiple campaigns**
```csv
Sample,Campaign,Lab,UTM_E,UTM_N,Cu,Pb,Au
S001,2023-Q1,Lab_A,305234,6201234,45.3,<5,0.125
S002,2023-Q1,Lab_A,305456,6201567,<10,8.4,<0.01
S003,2023-Q2,Lab_B,305678,6201890,78.9,<3,0.089
S004,2023-Q2,Lab_B,305901,6202213,123.4,<3,<0.005
S005,2024-Q1,Lab_C,306124,6202537,<10,12.6,0.234
```

**Notes:**
- Multiple labs → different LODs detected automatically
- Extra columns (Campaign, Lab) are ignored in analysis but preserved
- Different LODs per element handled correctly

---

## ❌ Common Errors and Solutions

### **Error 1: Using semicolon (;) instead of comma (,)**

❌ **Incorrect:**
```csv
Sample;Cu;Zn;Pb
S001;45.3;120.5;8.2
```

✅ **Correct:**
```csv
Sample,Cu,Zn,Pb
S001,45.3,120.5,8.2
```

**Solution:** In Excel, when saving choose "CSV (Comma delimited)" not "CSV (Semicolon delimited)"

---

### **Error 2: Using comma as decimal separator**

❌ **Incorrect:**
```csv
Sample,Cu
S001,"45,3"
```

✅ **Correct:**
```csv
Sample,Cu
S001,45.3
```

**Solution:** Use point (`.`) as decimal separator, not comma (`,`)

---

### **Error 3: Values below LOD without `<` symbol**

❌ **Incorrect:**
```csv
Sample,Cu
S001,below LOD
S002,BDL
S003,nd
S004,not detected
```

✅ **Correct:**
```csv
Sample,Cu
S001,<5
S002,<5
S003,<5
S004,<5
```

---

### **Error 4: Mixing LOD formats**

❌ **Inconsistent:**
```csv
Sample,Cu
S001,<5
S002,less than 5
S003,<10
S004,ND
```

✅ **Correct:**
```csv
Sample,Cu
S001,<5
S002,<5
S003,<10
S004,<5
```

**Note:** Different LODs are OK (like `<5` and `<10`), but always use `<value` format

---

### **Error 5: Including units in values**

❌ **Incorrect:**
```csv
Sample,Cu
S001,45.3 ppm
S002,<5 ppm
```

✅ **Correct:**
```csv
Sample,Cu
S001,45.3
S002,<5
```

**Note:** Units should be in documentation, not in data values

---

## 🔧 How to Prepare Your Data

### **From Excel:**

1. **Organize your data:**
   - Column 1: Sample IDs
   - Columns 2-3: Coordinates (optional)
   - Remaining columns: Chemical elements

2. **Clean values below LOD:**
   - Find: "BDL", "below LOD", "nd", "not detected", etc.
   - Replace with: `<5` (using your actual LOD)

3. **Remove units:**
   - Find: " ppm", " ppb", " wt%", etc.
   - Replace with: (nothing)

4. **Save as CSV:**
   - File → Save As
   - Type: **CSV (Comma delimited) (*.csv)**
   - ⚠️ DO NOT use "CSV UTF-8" if you have problems

---

### **From Google Sheets:**

1. Organize your data as in Excel
2. File → Download → Comma-separated values (.csv)

---

## 📏 Limits and Recommendations

| Aspect | Minimum | Recommended | Maximum |
|--------|---------|-------------|---------|
| **Number of samples** | 5 | 20+ | No practical limit |
| **Chemical elements** | 1 | 5-15 | No limit |
| **% Values below LOD** | 1% | 10-30% | 50%* |
| **File size** | - | < 10 MB | 100 MB |

\* With >50% censoring, consider non-parametric methods or review analytical design

---

## 🧪 CSV Validation

### **Checklist before processing:**

- [ ] First row has column names
- [ ] Numeric values use point (`.`) as decimal
- [ ] Values below LOD have `<value` format
- [ ] Coordinates in separate columns (if using IDW)
- [ ] No cells with mixed text (e.g., "45.3 ppm")
- [ ] File saved as `.csv` (not `.xlsx`)
- [ ] No special characters in column names
- [ ] No empty rows or columns
- [ ] Consistent LOD notation throughout

---

## 💾 File Location

### **Option 1: Specific folder (recommended)**
```
lod-imputation-geochem/
└── data/
    └── raw/
        └── my_geochem_data.csv  ← Here
```

### **Option 2: Same folder as scripts**
```
lod-imputation-geochem/
├── lod_imputation/
├── scripts/
└── my_geochem_data.csv  ← Here
```

---

## 🚀 Using Your Data
```python
from lod_imputation import cargar_csv, detectar_lod, extraer_coordenadas, aplicar_reemplazo_lod

# Load data
df = cargar_csv('data/raw/my_geochem_data.csv')

# Detect LODs automatically
df_clean, lod_info = detectar_lod(df)

# Separate coordinates
df_geo, df_coords = extraer_coordenadas(df_clean)

# Apply imputation method
df_result, log = aplicar_reemplazo_lod(
    df_geo, 
    lod_info, 
    method="beta"  # or "simple", "lrem", "idw"
)

# Save results
df_result.to_csv('data/processed/imputed_data.csv', index=False)
```

---

## 📞 Quick Summary

**Your CSV must have:**
1. ✅ Headers in first row
2. ✅ Numeric values with point decimal
3. ✅ Values below LOD as `<5`, `<0.01`, etc.
4. ✅ (Optional) Coordinates in separate columns
5. ✅ UTF-8 or ASCII encoding

**Methods available based on your data:**
- Without coordinates: Simple, β-substitution, lrEM
- With coordinates: ALL methods including IDW

---

## 🎓 Complete Downloadable Example
```csv
Sample_ID,Date,UTM_E,UTM_N,Cu,Zn,Pb,Au,Ag,As,Mo
DDH-001-01,2024-01-15,305234.5,6201234.8,125.3,85.2,<5,0.125,1.8,<3,<2
DDH-001-02,2024-01-15,305240.2,6201240.5,<10,<50,8.4,<0.01,<0.5,4.2,<2
DDH-001-03,2024-01-15,305246.8,6201246.1,245.7,150.3,12.6,0.089,2.5,<3,3.1
DDH-002-01,2024-01-16,306124.3,6202536.9,<10,210.7,<5,0.234,<0.5,5.8,<2
DDH-002-02,2024-01-16,306130.1,6202542.6,456.2,<50,25.8,<0.01,4.2,8.3,6.5
DDH-002-03,2024-01-16,306135.8,6202548.3,<10,95.5,<5,0.156,<0.5,<3,<2
DDH-003-01,2024-01-17,307015.2,6203425.1,89.4,165.8,<5,<0.01,1.9,<3,<2
DDH-003-02,2024-01-17,307021.9,6203430.8,<10,<50,18.3,0.067,<0.5,6.1,4.2
```

Copy this example, paste it into Excel/Google Sheets, and save as CSV to test the system.

---

## 🆘 Validation Tool

Before processing your data, use the validation tool:
```bash
python scripts/04_validar_csv.py your_data.csv
```

This will check:
- ✅ File format
- ✅ Column structure
- ✅ LOD notation
- ✅ Data types
- ✅ Coordinate presence
- ✅ Available methods

---

**Last updated**: 2024-12-01  
**Version**: 1.0