# 🏆 CS2 Professional Players Data Analytics Pipeline

A robust, end-to-end data science project evaluating the top 25 global CS2 players through rigorous cleaning, statistical normalization, and interactive visualization.

---

## 1. Problem & Target User
* **The Problem**: In the high-stakes world of CS2 esports, raw performance data is often fragmented across multiple platforms. Inconsistencies like missing values (`--`) and diverse data formats make it impossible for teams to compare players on a truly "level playing field."
* **Target User**: 
    * **Pro Coaches**: Looking to benchmark their roster against global rivals.
    * **Data Analysts**: Requiring clean, normalized datasets for recruitment scouting.
    * **Hardcore Fans**: Seeking objective metrics beyond simple K/D ratios.

---

## 2. Data Specifications
* **Dataset Scope**: High-fidelity simulated data covering the world's elite teams as of April 2026: **Vitality, NAVI, Astralis, The MongolZ, and Aurora**.
* **Key Attributes**:
    * **Primary Metrics**: `Rating 2.1` (the gold standard of CS2 performance).
    * **Technical Dimensions**: `Firepower` (aim proficiency), `Utility` (grenade impact), `Entry` (first-kill aggression), and `Clutch` (1-vs-X win probability).
    * **Specialized Roles**: Dedicated tracking for `AWP` (Sniper) and `Opening` (Success in round-start duels).

---

## 3. Methods & Pipeline Architecture
1.  **Stage 1: Exploration**: Automated scanning for "Dirty Data" (Strings in numeric columns).
2.  **Stage 2: Intelligent Cleaning**: Instead of deleting rows with missing Ratings, we apply **Team-Based Mean Imputation**. This uses the collective performance of the player's teammates to estimate missing values, preserving the sample size of 25.
3.  **Stage 3: Feature Engineering**:
    * **Combat Index**: A custom weighted formula: `(Firepower*0.4 + Entry*0.3 + Clutch*0.3)`.
    * **Z-Score Normalization**: Standardizing Ratings to identify "Outliers" (Superstars) who deviate significantly from the mean.
4.  **Stage 4: Role Logic**: Algorithmic classification into `Sniper`, `Tactical IGL`, or `Rifler` based on equipment usage thresholds.

---

## 4. Key Strategic Findings
* **Performance Equalization**: By restoring 12% of missing data via imputation, we unlocked a complete ranking for players like *phzy* and *ryu* who were previously "invisible" due to data gaps.
* **The "Star" Disparity**: Z-Score analysis revealed that elite players (e.g., *ZywOo*) operate **2.5+ standard deviations** above the average, quantifying their "game-breaking" potential.
* **Role Clustering**: Scatter matrix analysis confirmed a negative correlation between high `Utility` and `Entry` scores, highlighting the distinct sacrifice tactical leaders make for their team's entry fraggers.

---

## 5. Deployment & Execution
1.  **Environment**: Requires **Python 3.8** or higher.
2.  **Dependency Installation**:
    ```bash
    pip install streamlit pandas matplotlib seaborn numpy
    ```
3.  **Local Launch**:
    ```bash
    streamlit run app.py
    ```
4.  **Network Access**: The dashboard will automatically serve on `http://localhost:8501`.

---

## 6. Project Demo & Repository
* **Interactive Dashboard**: (https://cutesunday.streamlit.app)
* **Source Code**: (https://github.com/20060314zt-max/2468213-acc102-data-product)
* **Documentation**: Includes full Python source code and the logic behind the Combat Index weights.

---

## 7. Limitations & Roadmap
* **Current Limitations**: 
    * The model currently focuses exclusively on the **Global Top 5 Teams**.
    * Economic data (Equipment Value vs. Round Outcome) is not yet integrated.
* **Future Roadmap**:
    1.  **Real-Time Integration**: Connecting to the HLTV/PandasScore API for live tournament updates.
    2.  **Advanced Visualization**: Adding interactive Radar Charts to compare two players head-to-head.
    3.  **Predictive Analytics**: Implementing Machine Learning to forecast "Match MVP" probability based on mid-game stats.



