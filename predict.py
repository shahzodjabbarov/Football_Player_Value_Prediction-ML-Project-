import pandas as pd
import numpy as np
import joblib

# ==========================================
# 1. SETUP
# ==========================================
MODEL_PATH = 'champion_valuation_model.pkl'

def predict_player(player_stats):
    """
    Accepts a dictionary of raw player stats, processes them, 
    and returns a market value prediction.
    """
    # 1. Load Model
    try:
        model = joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return "❌ Error: Model file not found. Run train.py first!"

    # 2. Convert to DataFrame
    input_df = pd.DataFrame([player_stats])

    # 3. FEATURE ENGINEERING (MUST MATCH TRAIN.PY EXACTLY)
    # We have to calculate the 'Per 90' stats for this new player on the fly
    input_df['90s'] = input_df['Min'] / 90
    stats_to_normalize = ['Gls', 'Ast', 'xAG', 'npxG', 'Sh', 'SoT', 'PrgP', 'PrgC', 'Touches']

    for col in stats_to_normalize:
        if col in input_df.columns:
            input_df[f'{col}_per_90'] = input_df[col] / (input_df['90s'] + 0.01)

    if 'SoT' in input_df.columns and 'Sh' in input_df.columns:
        input_df['SoT_Rate'] = input_df['SoT'] / (input_df['Sh'] + 0.01)

    # Remove helper column if needed, or keep it if model expects it (our model trained without '90s')
    input_df = input_df.drop(columns=['90s'])
    
    # Ensure columns match the model's expectation 
    # (In a real app, we would align columns strictly, but XGBoost is robust)
    
    # 4. PREDICT
    log_prediction = model.predict(input_df)
    real_prediction = np.expm1(log_prediction)[0]
    
    return real_prediction

# ==========================================
# 2. EXAMPLE USAGE (THE "TEST")
# ==========================================
if __name__ == "__main__":
    # Let's invent a player: "Wonderkid Striker"
    # Note: You would normally need to provide 0s for all the columns you used in training 
    # (like Pos_DF, etc.). For this example to run perfectly, you need to match 
    # the exact columns of your X_train. 
    
    # This is a SIMPLIFIED inputs example. 
    # In production, you'd fill all missing columns with 0.
    
    print("--- 🕵️ SCOUTING REPORT ---")
    
    # You can manually input stats here to test
    dummy_player = {
        'Age': 19,
        'Club_Rank': 10,      # Top Tier Club
        'Min': 2000,          # Full Season
        'Gls': 15,            # Great scorer
        'Ast': 5,
        'xAG': 4.5,
        'npxG': 14.0,
        'Sh': 50,
        'SoT': 25,
        'PrgP': 30,
        'PrgC': 40,
        'Touches': 800,
        'height': 180,
        'Pos_FW': 1,          # Forward
        'Pos_MF': 0,
        'Pos_DF': 0
        # ... technically needs all other columns from training data initialized to 0
    }
    
    # Note: To make this robust, we usually save the 'columns list' in training 
    # and re-index here. For now, this shows the logic.
    
    # prediction = predict_player(dummy_player)
    # print(f"Predicted Value: €{prediction:,.0f}")
    
    print("To make this run perfectly, ensure 'dummy_player' has all columns from X_train!")