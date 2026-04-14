CS2 Professional Players Data Analytics Pipeline
## 1. Problem & Target User
* **Problem Statement**: CS2 match data is often voluminous and unstructured.
* **Target User**: Esports coaches and analysts.

---

## 2. Data
* **Source**: Simulated data from elite global CS2 circuits.
* **Key Fields**: Player, Team, Rating, and Technical Metrics.

---

## 3. Methods
1. **Data Exploration**: Identifying anomalous placeholders.
2. **Data Cleaning**: Imputation based on Team Average Rating.
3. **Feature Engineering**: Combat_Index and Z-Score.
4. **Data Visualization**: Dual-layer interactive Streamlit interface.

---

## 4. Key Findings
* **Global Benchmarking**: Direct cross-team horizontal comparison.
* **Data Correction**: Restored 12% of missing data points.
* **Elite Performance**: Identified star players via Z-Score.

---

## 5. How to Run
1. Ensure **Python 3.8+** is installed.
2. Install dependencies:  
   `pip install streamlit pandas matplotlib seaborn numpy`
3. Execute in terminal:  
   `streamlit run app.py`
4. Access browser at `http://localhost:8501`.

---

## 6. Product Link / Demo
* **Live Demo**: [https://cutesunday.streamlit.app](https://cutesunday.streamlit.app)
* **GitHub Repository**: (https://github.com/20060314zt-max/2468213-acc102-data-product)

---

## 7. Limitations & Next Steps
* **Limitations**: Dataset restricted to World's Top 5 teams.
* **Next Steps**:
    1. Integrate Real-Time APIs.
    2. Develop HR Efficiency module.
    3. Implement advanced Radar Charts.


