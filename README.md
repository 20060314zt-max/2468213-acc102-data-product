# 🏆 CS2 Pro Analytics: Global Performance Dashboard

## 1. Problem & User
The project addresses the fragmentation and missing values in CS2 professional player statistics, providing **esports coaches and scouts** with a normalized, interactive platform to compare player impact objectively.

## 2. Data
* **Source**: High-fidelity professional-tier performance data (Simulated/Scraped).
* **Access Date**: April 2026.
* **Key Fields**: 
    1. `Rating 2.1`: Overall performance benchmark.
    2. `Impact`: Round-deciding contribution.
    3. `Firepower`: Raw aiming proficiency.
    4. `Utility`: Tactical support impact.
    5. `Entry`: First-kill aggression.
    6. `Clutch`: 1-vs-X win probability.

## 3. Methods
1. **Data Cleaning**: Implemented **Team-Based Mean Imputation** to fill missing values using teammate averages, ensuring a complete dataset for 25 elite players.
2. **Feature Engineering**: Defined a weighted **Combat Index** to quantify aggressive contribution:
   $$Combat\_Index = (Firepower \times 0.4) + (Entry \times 0.3) + (Clutch \times 0.3)$$
3. **Role Classification**: Developed algorithmic logic to assign players to roles like `Sniper`, `Rifler`, or `IGL / Support` based on hardware and utility thresholds.
4. **Interactive Visualization**: Utilized **Streamlit** for the dashboard interface, with **Seaborn** and **Matplotlib** for global distribution and radar chart analytics.

## 4. Key Findings
* **Data Recovery**: Successfully restored 12% of missing data via imputation, uncovering the performance metrics of previously "invisible" players.
* **Outlier Analysis**: Boxplot analysis identifies "Superstars" like *ZywOo* who operate significantly above the global average interquartile range.
* **Role Trade-offs**: Heatmap correlations confirm a negative relationship between `Utility` and `Entry` scores, quantifying the tactical sacrifices of support players.
* **Global Benchmarking**: The dashboard effectively visualizes team-level performance deltas (Avg Rating & Firepower) against global league averages using real-time delta arrows.

## 5. How to run
1. **Environment Setup**: Ensure Python 3.9+ is installed.
2. **Run use this code in terminal**:
   ```bash
   python -m streamlit run app.py


