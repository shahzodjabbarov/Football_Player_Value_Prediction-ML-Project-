import pandas as pd

# ============================================
# 1. LOAD DATASETS
# ============================================

df_fbref = pd.read_csv(
    "hf://datasets/3zden/fbref_football_player_performance_2024-2025/PlayersFBREF.csv"
)

df_transfermarkt = pd.read_csv("players.csv")

print(f"FBRef players: {len(df_fbref)}")
print(f"Transfermarkt players: {len(df_transfermarkt)}")

# ============================================
# 2. CLEAN NAMES (FOR MATCHING ONLY)
# ============================================

def clean_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()

    replacements = {
        'ü': 'u', 'ö': 'o', 'ä': 'a',
        'ã': 'a', 'á': 'a', 'à': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u',
        'ñ': 'n', 'ç': 'c'
    }

    for k, v in replacements.items():
        name = name.replace(k, v)

    name = name.replace('.', '').replace('-', ' ')
    name = ' '.join(name.split())

    return name.strip()

df_fbref["name_clean"] = df_fbref["Player"].apply(clean_name)
df_transfermarkt["name_clean"] = df_transfermarkt["name"].apply(clean_name)

# ============================================
# 3. REMOVE DUPLICATE HUMAN NAME
# ============================================

# We keep FBRef's "Player" as the single name column
df_transfermarkt = df_transfermarkt.drop(columns=["name"], errors="ignore")

# ============================================
# 4. MERGE EVERYTHING (NO COLUMN FILTERING)
# ============================================

df_merged = df_fbref.merge(
    df_transfermarkt,
    on="name_clean",
    how="inner",
    suffixes=("_fbref", "_tm")
)

print(f"Matched players: {len(df_merged)}")

# ============================================
# 5. SAVE FULL MERGED DATASET
# ============================================

output_file = "players_merged_all_columns.csv"
df_merged.to_csv(output_file, index=False)

print(f"Saved file: {output_file}")
print(f"Rows: {len(df_merged)}")
print(f"Columns: {len(df_merged.columns)}")

# ============================================
# 6. OPTIONAL: SHOW COLUMN LIST ONCE
# ============================================

pd.set_option("display.max_columns", 200)
print("\nColumns in merged file:")
print(df_merged.columns.tolist())
