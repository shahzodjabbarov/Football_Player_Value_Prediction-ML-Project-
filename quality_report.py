import pandas as pd
import numpy as np

# ============================================
# 1. LOAD DATA
# ============================================

df = pd.read_csv("players_merged_all_columns.csv")

print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

# ============================================
# 2. BASIC CLEANUPS FOR INSPECTION
# ============================================

# Fix numeric columns that may be strings
if "Minutes" in df.columns:
    df["Minutes"] = (
        df["Minutes"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace("nan", np.nan)
        .astype(float)
    )

# ============================================
# 3. DATA QUALITY REPORT
# ============================================

report_rows = []

n_rows = len(df)

for col in df.columns:
    series = df[col]

    missing_count = series.isna().sum()
    missing_pct = (missing_count / n_rows) * 100
    unique_count = series.nunique(dropna=True)

    row = {
        "column": col,
        "dtype": str(series.dtype),
        "rows": n_rows,
        "missing_count": missing_count,
        "missing_pct": round(missing_pct, 2),
        "unique_values": unique_count,
        "example_1": series.dropna().iloc[0] if unique_count > 0 else None,
        "example_2": series.dropna().iloc[1] if unique_count > 1 else None,
        "example_3": series.dropna().iloc[2] if unique_count > 2 else None,
    }

    # Numeric stats
    if pd.api.types.is_numeric_dtype(series):
        row.update({
            "min": series.min(),
            "max": series.max(),
            "mean": series.mean(),
            "std": series.std(),
            "zeros": int((series == 0).sum())
        })
    else:
        row.update({
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "zeros": None
        })

    report_rows.append(row)

df_report = pd.DataFrame(report_rows)

# ============================================
# 4. SORT FOR EASY REVIEW
# ============================================

df_report = df_report.sort_values(
    by=["missing_pct", "unique_values"],
    ascending=[False, True]
)

# ============================================
# 5. SAVE REPORT
# ============================================

output_file = "data_quality_report.csv"
df_report.to_csv(output_file, index=False)

print(f"\nSaved data quality report to: {output_file}")

# ============================================
# 6. QUICK TERMINAL SUMMARY
# ============================================

print("\nColumns with missing data:")
print(
    df_report[df_report["missing_count"] > 0][
        ["column", "missing_count", "missing_pct"]
    ]
)

print("\nColumns with only one unique value (likely useless):")
print(
    df_report[df_report["unique_values"] <= 1][
        ["column", "unique_values"]
    ]
)

print("\nHigh-cardinality columns (likely IDs / URLs):")
print(
    df_report[df_report["unique_values"] > n_rows * 0.9][
        ["column", "unique_values"]
    ]
)
