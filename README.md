# Moneyball AI: Predicting Football Player Market Value

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange?style=for-the-badge)
![Scikit-Learn](https://img.shields.io/badge/Library-Scikit_Learn-yellow?style=for-the-badge)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=for-the-badge)

## 📊 Executive Summary
This project leverages Machine Learning to predict the market value of professional football players in the Top 5 European Leagues. By analyzing over **2,500 players** and **50+ performance metrics**, we built a valuation engine that outperforms traditional linear modeling by **31%**.

**Key Results:**
* **R-Squared:** `0.70` (Variance Explained)
* **Mean Absolute Error (MAE):** `€4.9M`
* **Impact:** The model accurately identifies undervalued talent by separating "Hype" (Club Prestige) from "Performance" (Per 90 stats).

---

## 🧠 The Methodology
The project followed a rigorous Data Science pipeline, moving from raw data to a production-grade XGBoost model.

### 1. Data Processing & Engineering
Raw player data is messy. We didn't just clean it; we engineered it.
* **Handling Missing Data:** Imputed physical traits (Height/Weight) based on **Positional Medians** (e.g., filling missing Center Back heights with the avg Center Back height, not the global avg).
* **Smart Features:** Created **"Per 90"** metrics (Goals/90, xG/90) to normalize data between starters and bench players.
* **Log Transformation:** Applied `Log1p` to the target variable (`Value`) to handle the massive skew caused by elite superstars (e.g., Mbappe, Haaland).

### 2. Model Evolution
We tested three distinct architectures to find the optimal fit.

![Model Comparison Chart](model_comparison.png)

* **Linear Regression:** Baseline model. Failed to capture non-linear relationships (e.g., Age vs Value).
* **Random Forest:** Huge improvement. Successfully captured the importance of "Club Rank."
* **XGBoost (Tuned):** The Champion. After Hyperparameter Tuning (Grid Search), this model achieved the lowest error rate by effectively penalizing outliers.

---

## 🔍 Key Insights & Discoveries

### 1. What actually drives price?
Contrary to popular belief, raw goals aren't the #1 driver. **Context is King.**
Our model discovered that **Club Prestige (Rank)** is the single strongest predictor of value, followed by **Age** and **Minutes Played**. Performance metrics (`xG`, `Progressive Passes`) act as multipliers on top of this base.

![Feature Importance Chart](feature_importance.png)

### 2. The "Ball-Playing Defender"
Correlation analysis revealed distinct valuation logic for different positions:
* **Forwards:** Valued on `xG` (Expected Goals) and `Shots on Target`.
* **Defenders:** Valued on `Progressive Passes` and `Touches`. *Tackles and Clearances had almost zero correlation with high market value.*

---

## 📈 Results: The Truth Plot
Below is the performance on the Test Set (20% of unseen data). The model shows high fidelity for players valued between **€1M - €50M**.
* *Note: The model remains conservative on "Superstar" outliers (>€100M), consistently predicting them in the €80M-€100M range due to the scarcity of training examples at that tier.*

![Prediction Scatter Plot](prediction_scatter.png)

---

## 🛠️ Tech Stack
* **Core:** Python, Pandas, NumPy
* **ML:** Scikit-Learn, XGBoost
* **Viz:** Matplotlib, Seaborn
* **Tuning:** RandomizedSearchCV

## 🚀 Future Work
* **The "Elite" Module:** Train a separate binary classifier to detect "Superstars" and route them to a specialized model trained only on high-value players.
* **Social Sentiment:** Integrate Twitter/Instagram follower counts as a feature to capture "Marketing Value" which the current stats-based model misses.

---
*Author: [Your Name]*
*Dataset: 2024/2025 Season Data (Top 5 Leagues)*
