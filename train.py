import pandas as pd
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# ==========================================
# 1. CONFIGURATION
# ==========================================
DATA_PATH = 'FINAL_TRAINING_DATA.csv'  # Make sure this file is in the same folder!
MODEL_PATH = 'champion_valuation_model.pkl'

def train_model():
    print("--- ⚽ STARTING TRAINING PIPELINE ---")
    
    # 1. LOAD DATA
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"✅ Loaded {len(df)} players from {DATA_PATH}")
    except FileNotFoundError:
        print(f"❌ Error: Could not find {DATA_PATH}. Please check the file path.")
        return

    # 2. FEATURE ENGINEERING ("Smart Stats")
    # We must replicate this exactly in predict.py later!
    print("⚙️ Engineering features...")
    df['90s'] = df['Min'] / 90
    stats_to_normalize = ['Gls', 'Ast', 'xAG', 'npxG', 'Sh', 'SoT', 'PrgP', 'PrgC', 'Touches']

    for col in stats_to_normalize:
        if col in df.columns:
            df[f'{col}_per_90'] = df[col] / (df['90s'] + 0.01)

    if 'SoT' in df.columns and 'Sh' in df.columns:
        df['SoT_Rate'] = df['SoT'] / (df['Sh'] + 0.01)

    # 3. IMPUTATION
    # Simple median filling for the pipeline
    if 'height' in df.columns:
        df['height'] = df['height'].replace(0, df['height'].median())
    
    for col in ['Touches', 'Cmp', 'Att', 'Rec']:
        if col in df.columns:
            df[col] = df[col].replace(0, df[col].median())

    # 4. PREPARE X and y
    # Log transform the target to handle elite outliers
    X = df.drop(columns=['value', '90s'])
    y = np.log1p(df['value'])

    # 5. SPLIT
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. TRAIN
    print("🏋️ Training XGBoost Model (This may take a moment)...")
    model = XGBRegressor(
        n_estimators=1500,
        learning_rate=0.01,
        max_depth=3,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42
    )
    model.fit(X_train, y_train)

    # 7. EVALUATE
    y_pred_log = model.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    y_test_real = np.expm1(y_test)

    mae = mean_absolute_error(y_test_real, y_pred)
    r2 = r2_score(y_test_real, y_pred)

    print(f"\n--- 🏆 RESULTS ---")
    print(f"R-Squared: {r2:.4f}")
    print(f"Mean Error: €{mae:,.0f}")

    # 8. SAVE
    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()