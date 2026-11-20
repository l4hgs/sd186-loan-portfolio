# Project SD-186: Synthetic Loan Portfolio Performance Data Model

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Framework: PFRS 9 / IFRS 9](https://img.shields.io/badge/Compliance-BSP%20Circular%201011%20%7C%20PFRS%209-orange.svg)](https://www.bsp.gov.ph/)
[![Domain: Banking & Risk](https://img.shields.io/badge/Domain-Philippine%20Universal%20Banking-purple.svg)](#)

**Eskwelabs Data Innovation Fellowship (Cohort 11, Data Modeling Track)**  
**Author:** Ricco Cantos & Danver Manalo | **Domain:** Banking & Finance | **Currency:** Philippine Peso (PHP, ₱)  
**Primary Persona:** Credit Analyst / Finance Risk Analyst

---

## 1. Executive Summary & Problem Framing

**Project SD-186** implements a multi-table relational synthetic credit portfolio servicing engine modeled after a Philippine universal bank. DENOMINATED exclusively in **Philippine Pesos (PHP, ₱)**, the portfolio captures consumer installment lending, vehicle financing, residential mortgages, and SME commercial facilities across a **42-month multi-regime simulation lifecycle**:

- **Warm-Up Horizon ($t \in [-6, -1]$, July 2022 – December 2022):** Seasons the credit portfolio so loans enter observation with realistic initial Days Past Due ($DPD$), unobserved delinquency history, and seasoned Loan-to-Value ($LTV$) ratios (trimmed pre-export).
- **Observation Horizon ($t \in [0, 35]$, January 2023 – December 2025):** 36 calendar months of monthly servicing ledgers, payment transactions, and default workout resolutions published for analysis.

The data generation pipeline addresses three primary banking analytics objectives:

1. **PFRS 9 / IFRS 9 Multi-Stage ECL Reserving & Migration:** Modeling forward-looking credit risk transitions, Significant Increase in Credit Risk (SICR) staging, and lifetime Expected Credit Loss (ECL) balance sheet provisions.
2. **Predictive Risk Modeling Under Extreme Imbalance:** Benchmarking regularized linear models against tree ensembles on rare-event out-of-time test partitions ($0.200\%$ default prevalence).
3. **Causal Confounding & Omitted-Variable Evaluation:** Modeling true data mechanics through unobserved latent traits—borrower cash-flow resilience $U(i)$, shadow/informal debt $W(i)$, and macroeconomic tightening stress $Z_{\text{macro}}(t)$—and subsequently censoring them pre-export to quantify omitted-variable bias in external scorecards.

---

## 2. Repository Structure

```text
SD-186_Notebook/
├── README.md                                          # Project overview, architecture & setup guide
├── requirements.txt                                   # Python dependencies (NumPy, Pandas, Scikit-Learn)
├── .gitignore                                         # Git ignore rules for virtualenvs, checkpoints & cache
├── docs/
│   └── SD-186_Model_Research_and_Specifications.md    # Master publication-ready model research & specs
├── notebooks/
│   ├── 01_synthetic_data_generator.ipynb              # Notebook 1: DAG generator, assertions & CSV export
│   └── 02_portfolio_eda_and_risk_modeling.ipynb       # Notebook 2: Vintages, roll-rates, IFRS 9 & ML modeling
├── src/
│   ├── __init__.py
│   ├── config.py                                      # Global parameters (LOCKED, CALIBRATED, ASSUMED)
│   ├── generators.py                                  # Vectorized DAG generators & panel simulation loop
│   └── validators.py                                  # Integrity assertions, latent scrubber & calibration
├── data/
│   ├── raw_export/                                    # Clean 7 exported catalog CSV tables (0 latent leaks)
│   │   ├── Borrowers.csv                              # 6,000 borrower profiles
│   │   ├── CreditScores.csv                           # 84,000 quarterly bureau score records
│   │   ├── Loans.csv                                  # 9,927 originated loan accounts
│   │   ├── Collateral.csv                             # 5,467 pledged collateral assets
│   │   ├── RepaymentSchedules.csv                     # 176,178 monthly servicing records
│   │   ├── Payments.csv                               # 176,178 cash settlement transactions
│   │   └── DelinquencyEvents.csv                      # 1,317 default and recovery workout episodes
│   └── diagnostics/
│       ├── calibration_summary.json                   # 1,000-borrower smoke test diagnostic logs
│       └── calibration_summary_full_6k.json           # 6,000-borrower production calibration summary
└── outputs/
    └── figures/                                       # High-resolution charts from Notebook 2
        ├── vintage_curves_by_product.png              # Workflow 1: Cumulative 90+ DPD by MOB 0-24
        ├── dpd_roll_rate_heatmap.png                  # Workflow 2: Month-over-month roll-rate matrix
        ├── ifrs9_ecl_trajectory.png                   # Workflow 3: Multi-stage ECL provisions over time
        └── model_roc_pr_curves.png                    # Workflow 4: Out-of-time ML ROC-AUC and PR-AUC curves
```

---

## 3. Product Portfolio Architecture

| Product Code | Segment Name               | Collateral Type  | Tenor Range | APR Range   | Increment | Mix Weight | Pricing & Security                    |
| :----------- | :------------------------- | :--------------- | :---------- | :---------- | :-------- | :--------- | :------------------------------------ |
| `PERSONAL`   | Personal Installment Loans | None (Unsecured) | 12–36 mos   | 18.0%–36.0% | ₱1,000    | 40.0%      | 100% Fixed / 100% Unsecured           |
| `AUTO`       | Auto Financing             | Vehicle Chattel  | 36–60 mos   | 9.0%–15.0%  | ₱10,000   | 25.0%      | 100% Fixed / 100% Secured             |
| `HOUSING`    | Residential Mortgages      | Residential REM  | 60–240 mos  | 6.5%–10.5%  | ₱50,000   | 15.0%      | 100% Floating Annual / 100% Secured   |
| `SME_WC`     | SME Working Capital        | Equipment / REM  | 12–48 mos   | 12.0%–22.0% | ₱10,000   | 20.0%      | 50% Fixed, 50% Floating / 70% Secured |

- **Collateral Reconciliation:** 100% of Auto (2,380) + 100% of Housing (1,444) + 69.89% of SME_WC (1,643) = **5,467 total collateralized loan facilities**, perfectly matching `Collateral.csv`.

---

## 4. Key Analytical Workflows & Empirical Results

The pipeline evaluates four core risk workflows executed in `notebooks/02_portfolio_eda_and_risk_modeling.ipynb` against the validated 6,000-borrower catalog:

### Workflow 1: Vintage Curves (Cumulative 90+ DPD by MOB 0–24)

- Confirms monotonic underwriting risk: $\text{Personal} > \text{SME Working Capital} > \text{Auto} > \text{Housing}$.
- Cumulative 90+ DPD default rate at MOB 24:
  - **Personal:** 28.42% (peak default hazard between MOB 9–15)
  - **SME Working Capital:** 10.78% (sensitive to inflation tightening)
  - **Auto:** 2.79% (inspected vehicle collateral anchoring)
  - **Housing:** 1.02% (prime real estate mortgage security)

### Workflow 2: Month-over-Month Delinquency Roll Rates

- **Current Persistence:** Current loans remain current with **99.27%** probability.
- **Roll Forward (30–59 $\to$ 60–89 DPD):** **26.81%** roll rate, strictly satisfying the BSP/industry calibration target of $25.0\% \text{ to } 40.0\%$ (`FLAG-02`).
- **Cure Rate:** **13.00%** of loans in DPD 30–59 cure back to fully current status.
- **Default Acceleration (60–89 $\to$ 90+ DPD):** **34.28%** roll forward into default, demonstrating the necessity of early intervention at DPD 30.
- **Absorbing Default State:** Defaulted loans (90+ DPD) show **99.33%** monthly persistence.

### Workflow 3: Prepayments, Collateral Workouts & IFRS 9 Staging

- **Prepayment Speeds (CPR):** Total prepaid principal of **₱345,345,681** in the observation window, yielding a monthly Single Monthly Mortality (SMM) of **0.543%** and an implied annualized **CPR of 6.32%** (within the 6%–14% target range). Prepayments show seasonal spikes in November and December from Philippine 13th-month bonus windfalls.
- **Collateral Workout Recovery:**
  - **Housing (Secured REM):** 90.07% recovery rate (realized LGD **9.93%**).
  - **SME Working Capital (Secured):** 84.15% recovery rate.
  - **Auto (Secured Chattel):** 57.49% recovery rate (depreciation and auction haircuts).
  - **Personal (Unsecured):** 18.20% recovery rate (realized LGD **81.80%**).
- **IFRS 9 Multi-Stage ECL:** Tracks Stage 2 (SICR) migrations peaking at **13.43%** during the monetary tightening shock ($t \in [10, 20]$), triggering required lifetime reserve expansion before stabilizing.

### Workflow 4: Out-of-Time 90+ DPD Machine Learning Benchmarking

- **Evaluation Window:** Chronological test split spanning `2025-06-01` to `2025-12-31` (32,514 active accounts, 65 defaults / **0.200%** positive prevalence).
- **Leakage Audit:** Explicit assertions verify zero next-month fields (`next_dpd`, `next_month`, `target_90p_next`) enter the feature matrices.

| Model Pipeline                                      | Out-of-Time ROC-AUC | Out-of-Time PR-AUC | Base Positive Rate | Lift vs. No-Skill |
| :-------------------------------------------------- | :-----------------: | :----------------: | :----------------: | :---------------: |
| **Logistic Regression (`class_weight='balanced'`)** |     **0.9982**      |     **0.5043**     |  0.0020 (0.200%)   |     **252x**      |
| **HistGradientBoostingClassifier**                  |     **0.9974**      |     **0.3408**     |  0.0020 (0.200%)   |     **170x**      |

- **Why Logistic Regression Outperformed GBDT on PR-AUC:** Delinquency progression follows smooth monotonic log-odds scaling across DPD and arrears. Regularized linear logistic regression avoids partitioning sparse positive cases (65 defaults across 32k rows) into small, noisy leaf bins, preserving superior probability calibration on the extreme right tail while satisfying BSP Circular No. 1011 explainability standards.

---

## 5. Calibration Summary (`FLAG-01` to `FLAG-05`)

All five acceptance criteria passed and are documented in `data/diagnostics/calibration_summary_full_6k.json`:

| Flag ID     | Quality Metric                  | Target Benchmark                                              | Full 6,000-Borrower Empirical Result                                  |  Audit Status  |
| :---------- | :------------------------------ | :------------------------------------------------------------ | :-------------------------------------------------------------------- | :------------: |
| **FLAG-01** | Cumulative Cohort 90+ DPD       | Personal (8–14%), SME (4–7%), Auto (2–4%), Housing (1–2.5%)   | Personal **12.02%**, SME **6.04%**, Auto **3.70%**, Housing **1.87%** |    **PASS**    |
| **FLAG-02** | DPD 30–59 $\to$ 60–89 Roll Rate | 25.0% to 40.0% monthly transition rate                        | **26.81%** (804 / 2,999 transitions)                                  |    **PASS**    |
| **FLAG-03** | Annualized Prepayment (CPR)     | 6.0% to 14.0% annualized CPR                                  | Full horizon check **8.29%**; Observation active book **6.32%**       |    **PASS**    |
| **FLAG-04** | Shock Window Stage 2 Share      | 8.0% to 18.0% active loan share in Stage 2 ($t \in [10, 20]$) | **13.43%** (7,074 / 52,676 active loan-months)                        |    **PASS**    |
| **FLAG-05** | ML Feature Separation           | ROC-AUC 0.72–0.82 (retaining latent unobserved variance)      | Observed features achieve **0.8852**; PR-AUC **0.5043**               | **CALIBRATED** |

---

## 6. Installation & Quickstart Guide

### Prerequisites

- Python 3.10, 3.11, 3.12, or 3.13
- Free standard data science stack (zero paid API keys required; Generative AI spend **₱0.00**):
  - `numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`, `scikit-learn`, `jupyter`, `ipykernel`

### Setup Steps

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd SD-186_Notebook
   ```

2. **Create & Activate Virtual Environment:**

   ```bash
   # On Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # On macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run Notebook 1 (Data Generation & Validation):**

   ```bash
   jupyter notebook notebooks/01_synthetic_data_generator.ipynb
   ```

   _Generates the full 7-table catalog in `data/raw_export/` and logs calibration results in `data/diagnostics/`._

5. **Run Notebook 2 (Portfolio EDA & Risk Modeling):**
   ```bash
   jupyter notebook notebooks/02_portfolio_eda_and_risk_modeling.ipynb
   ```
   _Executes Workflows 1–4, renders high-resolution charts in `outputs/figures/`, and evaluates ML out-of-time classifiers._

---

## 7. Compliance & License

- **Regulatory Framework:** Bangko Sentral ng Pilipinas (BSP) Circular No. 1011, Philippine Financial Reporting Standards 9 (PFRS 9 / IFRS 9), Basel III Accord.
- **Fellowship:** Eskwelabs Data Innovation Fellowship (Cohort 11).
- **License:** MIT License. Free for academic, educational, and professional risk research.
