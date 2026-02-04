import pandas as pd

df = pd.read_csv("players_merged_all_columns.csv")

# Drop junk index column if present
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# Drop rows with missing values in key columns
df = df.dropna(subset=[
    "market_value_in_eur",
    "height_in_cm",
    "foot"
])

print("Rows after dropping missing values:", len(df))

# Save cleaned version
df.to_csv("players_clean_no_missing.csv", index=False)
