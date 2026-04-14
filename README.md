CS2 Professional Players Data Analytics Pipeline
1. Problem & Target User
• Problem Statement: Professional esports (CS2) match data is often voluminous and unstructured. Raw datasets frequently contain missing values or inconsistent formatting (e.g., string placeholders like --), making comparative analysis difficult.
• Target User: Esports coaches, professional analysts, or hardcore players who require a centralized tool to compare the individual performance of the 25 core players from global top-tier teams on a unified baseline.
2. Data
• Source: Simulated data from elite global CS2 professional circuits (including Vitality, NAVI, Astralis, The MongolZ, and Aurora).
• Retrieval Date: 2026-04-14.
• Key Fields:
• Player/Team: Basic identification credentials.
• Rating: Core performance score (initially containing missing data denoted as --).
• Technical Metrics: Firepower, Utility, Entry, Clutch, Opening, and AWP usage levels.
3. Methods
1.	Data Exploration: Identifying anomalous placeholders (--) within raw data and detecting data type mismatches (Object vs. Float).
2.	Data Cleaning: Using Python pandas to convert anomalies into NaN and performing objective imputation based on Team Average Rating.
3.	Feature Engineering:
• Combat_Index: A weighted score blending firepower, entry-fragging, and clutching capabilities.
• Automated Role Labeling: Identifying "Snipers" or "Tactical Leads" based on AWP and Utility patterns.
• Z-Score Normalization: Calculating standard deviation of Ratings relative to the global sample mean.
4.	Data Visualization: Constructing a dual-layer interactive interface using Streamlit, featuring dynamic bar charts and multi-dimensional scatter matrices.
4. Key Findings
• Global Benchmarking: Facilitated a direct cross-team horizontal comparison of all 25 players, breaking the traditional roster-only view.
• Data Correction: Successfully restored 12% of missing data points through team-mean imputation, providing more reliable statistical rankings.
• Role Insight: The visualization matrix clearly distinguishes between "High Firepower" fraggers and "Tactical Support" players.
• Elite Performance: Identified top-tier star players whose performances significantly exceed the global mean via Z-Score analysis.
5. How to Run
1.	Ensure Python 3.8+ is installed.
2.	Install dependencies:
pip install streamlit pandas matplotlib seaborn numpy
3.	Execute in terminal:
streamlit run app.py
4.	Access the local port via browser (default: http://localhost:8501).
6. Product Link / Demo
• Live Demo: https://cutesunday.streamlit.app
• GitHub Repository: [Your GitHub Repository URL Here]
7. Limitations & Next Steps
• Limitations: The current dataset is restricted to the World's Top 5 teams and does not include historical win rates or economic management (Economy) data.
• Next Steps:
• Integrate Real-Time APIs for dynamic data updates.
• Develop a Human Resource Efficiency module to assess team composition stability.
• Implement advanced Radar Charts for multi-dimensional player attribute visualization.

