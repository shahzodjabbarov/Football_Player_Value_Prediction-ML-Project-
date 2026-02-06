import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# ================================
# 1. LOAD BOTH FILES
# ================================
current = pd.read_csv('current.csv')
fifa = pd.read_csv('fifa_players.csv')

print(f"Current data: {current.shape}")
print(f"FIFA data: {fifa.shape}")

# ================================
# 2. PREPARE NAME COLUMNS
# ================================

# Current data - use name_clean (already lowercase)
current['match_name'] = current['name_clean'].str.lower().str.strip()

# FIFA data - use both name and full_name
fifa['match_name'] = fifa['name'].str.lower().str.strip()
fifa['match_fullname'] = fifa['full_name'].str.lower().str.strip()

print("\nSample names from current:")
print(current['match_name'].head(10))

print("\nSample names from FIFA:")
print(fifa['match_name'].head(10))

# ================================
# 3. FUZZY MATCHING FUNCTION
# ================================

def find_best_match(name, fifa_names, threshold=80):
    """
    Find best matching FIFA player name using fuzzy matching
    threshold: minimum similarity score (0-100)
    """
    # Try matching with both name and full_name
    result = process.extractOne(name, fifa_names, scorer=fuzz.token_sort_ratio)
    
    if result and result[1] >= threshold:
        return result[0], result[1]  # (matched_name, score)
    else:
        return None, 0

# ================================
# 4. CREATE LOOKUP DICTIONARY
# ================================

# Combine FIFA name and full_name for matching
fifa_all_names = pd.concat([
    fifa['match_name'],
    fifa['match_fullname']
]).unique().tolist()

print(f"\nTotal unique FIFA names to match against: {len(fifa_all_names)}")

# ================================
# 5. MATCH PLAYERS
# ================================

matches = []
unmatched = []

print("\nMatching players (this may take 1-2 minutes)...")

for idx, row in current.iterrows():
    player_name = row['match_name']
    
    # Find best match
    matched_name, score = find_best_match(player_name, fifa_all_names, threshold=80)
    
    if matched_name:
        # Find in FIFA data (could be in name or full_name column)
        fifa_match = fifa[
            (fifa['match_name'] == matched_name) | 
            (fifa['match_fullname'] == matched_name)
        ]
        
        if not fifa_match.empty:
            matches.append({
                'original_name': row['Player'],
                'match_name': player_name,
                'fifa_matched_name': matched_name,
                'match_score': score,
                'current_idx': idx,
                'fifa_idx': fifa_match.index[0]
            })
        else:
            unmatched.append({'name': player_name, 'reason': 'Found match but not in FIFA data'})
    else:
        unmatched.append({'name': player_name, 'reason': 'No match found'})
    
    # Progress indicator
    if (idx + 1) % 100 == 0:
        print(f"Processed {idx + 1}/{len(current)} players...")

print(f"\nMatching complete!")
print(f"Matched: {len(matches)}")
print(f"Unmatched: {len(unmatched)}")

# ================================
# 6. MERGE DATASETS
# ================================

matches_df = pd.DataFrame(matches)

# Merge current data with FIFA data
merged = current.iloc[matches_df['current_idx']].reset_index(drop=True)
fifa_matched = fifa.iloc[matches_df['fifa_idx']].reset_index(drop=True)

# Add FIFA columns to current data
# Drop duplicate columns from FIFA (like name, age, etc.)
fifa_cols_to_add = [col for col in fifa.columns if col not in current.columns or col in [
    'crossing', 'finishing', 'heading_accuracy', 'short_passing', 'volleys',
    'dribbling', 'curve', 'freekick_accuracy', 'long_passing', 'ball_control',
    'acceleration', 'sprint_speed', 'agility', 'reactions', 'balance',
    'shot_power', 'jumping', 'stamina', 'strength', 'long_shots',
    'aggression', 'interceptions', 'positioning', 'vision', 'penalties',
    'composure', 'marking', 'standing_tackle', 'sliding_tackle',
    'overall_rating', 'potential', 'international_reputation(1-5)',
    'weak_foot(1-5)', 'skill_moves(1-5)'
]]

for col in fifa_cols_to_add:
    if col in fifa_matched.columns:
        merged[f'fifa_{col}'] = fifa_matched[col].values

# Add match score
merged['fuzzy_match_score'] = matches_df['match_score'].values

# ================================
# 7. SAVE RESULTS
# ================================

# Save merged file
merged.to_csv('players_newlist.csv', index=False)

print(f"\n SAVED: players_newlist.csv")
print(f"Shape: {merged.shape}")
print(f"Columns: {merged.shape[1]}")

# ================================
# 8. SHOW MATCHING QUALITY
# ================================

print("\n" + "="*60)
print("MATCHING QUALITY")
print("="*60)
print(f"Match score distribution:")
print(matches_df['match_score'].describe())

print(f"\nSample matches:")
sample = matches_df.sample(min(10, len(matches_df)))
for _, row in sample.iterrows():
    print(f"  {row['original_name']:30s} → {row['fifa_matched_name']:30s} (score: {row['match_score']})")

# ================================
# 9. SHOW UNMATCHED PLAYERS
# ================================

if unmatched:
    print("\n" + "="*60)
    print(f"UNMATCHED PLAYERS ({len(unmatched)})")
    print("="*60)
    unmatched_df = pd.DataFrame(unmatched)
    print(unmatched_df.head(20))
    
    # Save unmatched for review
    unmatched_df.to_csv('/content/drive/MyDrive/FOOTBALL_PLAYER_VALUE/unmatched_players.csv', index=False)
    print("\n SAVED: unmatched_players.csv")

print("\n" + "="*60)
print("NEW COLUMNS ADDED FROM FIFA:")
print("="*60)
new_cols = [col for col in merged.columns if col.startswith('fifa_')]
for col in new_cols:
    print(f"  - {col}")

print(f"\nTotal new columns: {len(new_cols)}")