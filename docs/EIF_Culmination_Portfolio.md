# EIF Culmination Portfolio: Synthetic Loan Portfolio Performance Data Model (SD-186)
**Eskwelabs Innovation Fellowship (EIF) Cohort 11 — Data Innovation Track**  
**Fellow:** Alodivinno Ricco L. Cantos  
**Collaborator:** John Danver Z. Manalo  
**Project Repository:** [https://github.com/l4hgs/sd186-loan-portfolio](https://github.com/l4hgs/sd186-loan-portfolio)  

---

## Slide 1: Title Slide

```
========================================================================================
                               EIF Culmination Portfolio
========================================================================================
                      Synthetic Loan Portfolio Performance Data Model
             PFRS 9 ECL Provisioning, Prepayment Dynamics, and Latent Confounding
                              in Philippine Banking (SD-186)

                         Presented by: Alodivinno Ricco L. Cantos
                    Eskwelabs Innovation Fellowship (EIF) — Cohort 11
                                  Data Innovation Track
========================================================================================
```

---

## Slide 2: About Me

* **Greeting & Profile:**  
  Hello! My name is **Ricco**, and I am a data science and analytics practitioner specializing in quantitative credit risk modeling, financial engineering, and synthetic data architectures.

* **My Interests:**
  * **Quantitative Risk & Banking Analytics:** Implementing PFRS 9 / IFRS 9 multi-stage ECL models, Basel III regulatory capital frameworks, and stress-testing engines.
  * **Probabilistic Data Synthesis:** Formulating structural causal models (SCMs), Directed Acyclic Graphs (DAGs), and vector-accelerated Monte Carlo simulations.
  * **Machine Learning for Imbalanced Credit Data:** Calibrating probability of default (PD) models, evaluating rare-event detection with Precision-Recall AUC (PR-AUC), and diagnosing omitted variable bias (OVB).
  * **End-to-End Pipeline Engineering:** Building reproducible, high-performance data pipelines with Python, NumPy, Pandas, and Scikit-Learn.
  * **Strategic Technology Research:** Exploring causal inference, algorithmic trading, and financial technology innovation.

* **What Motivates Me:**  
  *Bridging the gap between strict financial regulatory standards, machine learning, and privacy-preserving data access to empower ethical, high-impact financial decision-making.*

---

## Slide 3: My EIF Journey

* **Track:** Data Innovation  
* **Project:** Synthetic Data Modeling (SD-186)  

### About My Project
* **Project Overview:**  
  *Synthetic Loan Portfolio Performance Data Model* — Simulating a 42-month Philippine retail and commercial loan portfolio under macroeconomic stress to benchmark PFRS 9 expected credit loss (ECL) provisioning, prepayment mechanics, and latent confounding without exposing confidential customer banking records.

* **1. Data Blueprint:**  
  Architected a normalized 7-table relational schema across borrowers, bureau scores, loans, collateral, amortization schedules, payment transactions, and delinquency episodes. Embedded unobserved structural confounders—borrower resilience ($U_i$), shadow debt ($W_i$), and macro rate stress ($Z_t$)—that are scrubbed pre-export to induce realistic omitted variable bias.

* **2. Custom Generator:**  
  Engineered a modular, vector-accelerated Python simulation engine in Google Colab that scales from smoke testing (1,000 borrowers) to full production (6,000 borrowers, 9,927 loans, and 176,178 monthly cash-flow snapshots) across a 36-month exported window ($t \in [0, 35]$) with 100% referential integrity and PHP 0.00 AI text spend.

* **3. Business Analytics & ML:**  
  Built an end-to-end regulatory risk analytics suite in Google Colab evaluating product vintage curves, roll-rate transition persistence, multi-stage ECL reserve spikes during BSP monetary tightening, and out-of-time default classification under extreme class imbalance (0.200% default rate).

---

## Slide 4: Project Portfolio

### Project Title
**Synthetic Loan Portfolio Performance & Credit Risk Analytics (SD-186)**

* **Context:**  
  Commercial banks, FinTech lenders, and risk analytics teams need granular, multi-table loan performance and payment waterfall data to stress-test PFRS 9 expected credit losses, calibrate default scoring models, and audit operational clearing lags. However, real financial records are strictly protected under the Philippine Data Privacy Act of 2012 (RA 10173) and banking secrecy laws. SD-186 resolves this barrier by providing an empirically grounded, privacy-safe synthetic universe with realistic financial frictions.

* **My Role and Contributions:**  
  Served as **Lead Credit Risk Modeler & Synthetic Data Architect** (EIF Cohort 11 — Data Innovation Track):
  1. Spearheaded the mathematical formulation of the causal DAG and credit loss transition dynamics.
  2. Architected the 7-table relational schema ensuring point-in-time scoring updates and foreign key consistency.
  3. Engineered the vector-accelerated Monte Carlo data generation pipeline in Google Colab and local Python environments.
  4. Authored the regulatory risk analytics notebook and executive pitch deck evaluating PFRS 9 staging, roll rates, and machine learning under unobserved confounding.

---

## Slide 5: Outputs, Deliverables & Skills Demonstrated

### 4-Panel Executive Dashboard (Visuals)
* **Panel A — Cumulative 90+ DPD Vintage Curves by Product:**  
  Demonstrates clear risk stratification across MOB 0–24: Personal loans exhibit the highest default rate (**12.02%**; 451/3,752), followed by SME Working Capital (**6.04%**; 142/2,351), Auto (**3.70%**; 88/2,380), and secured Housing (**1.87%**; 27/1,444).
* **Panel B — Monthly IFRS 9 ECL Allowance Across Stress Window:**  
  Visualizes the **13.43% Stage 2 (SICR)** reserve surge during the Oct 2023–Aug 2024 BSP rate hike shock ($t=10$ to $20$), capturing lifetime expected loss provisioning on deteriorating credit profiles.
* **Panel C — Monthly Delinquency Roll-Rate Transition Heatmap:**  
  Quantifies credit state persistence: **26.81%** of accounts in DPD 30–59 roll forward into severe delinquency (DPD 60–89), while **13.00%** cure back to Current status, buoyed by Q4 13th-month bonus seasonal cash infusions.
* **Panel D — Out-of-Time ROC & Precision-Recall Curves:**  
  Evaluates rare-event default detection (0.200% test default rate): Class-balanced Logistic Regression achieves **0.5043 PR-AUC (252x lift)**, outperforming HistGradientBoosting (**0.3408 PR-AUC; 170x lift**) due to smooth log-odds calibration under extreme data sparsity.

### Key Deliverables Produced
1. **Relational Data Model Specification (Deliverable 1):**  
   Exhaustive 37-page mathematical research document defining the causal DAG, 7 physical tables, 8 regulatory formulas, and pre-export latent factor scrubbing ($U_i, W_i, Z_t$).
2. **Scalable Google Colab Synthetic Data Generator (Deliverable 2):**  
   Reproducible Python generator package (`01_synthetic_data_generator.ipynb`) generating 6,000 borrowers, 9,927 loans, and 176,178 servicing records with 22 automated integrity validations.
3. **Executive Analytics Suite & Presentation (Deliverable 3):**  
   End-to-end risk analytics notebook (`02_portfolio_eda_and_risk_modeling.ipynb`) and 13-slide executive presentation deck (`Project SD-186_ Deliverable 3b-1.pdf`) synthesizing PFRS 9 staging, CPR prepayment curves, and ML under unobserved confounding.

### Skills Demonstrated
* **Relational Schema Architecture & Causal Modeling:** Causal DAGs, 7-table foreign-key integrity, point-in-time scoring tables.
* **Probabilistic Monte Carlo Simulation:** Vectorized NumPy/Pandas pipelines, logit default probability equations, Merton structural credit models.
* **Banking Regulations & Accounting Standards:** IFRS 9 / PFRS 9 multi-stage ECL staging, BSP Circular No. 1011, Basel III capital requirements.
* **Rare-Event Machine Learning:** Imbalanced classification, Out-of-Time (OOT) temporal validation, Precision-Recall AUC (PR-AUC) optimization.
* **Operational Frictions Engineering:** Payment clearing lags (InstaPay/PESONet), NSF payment reversals, Missing at Random (MAR) credit bureau mechanisms.
* **Executive Data Storytelling:** Matplotlib, Seaborn, and C-suite technical communication.

---

## Slide 6: Reflection

### What I Learned
* **Decoupling Causal Drivers from Observational Data:**  
  Designing synthetic datasets for machine learning requires separating internal data-generating causal mechanisms (such as unobserved borrower resilience $U_i$ and shadow debt $W_i$) from exported catalog columns. Scrubbing latent confounders pre-export forces downstream predictive models to contend with authentic Omitted Variable Bias (OVB), preventing models from exploiting trivial formula inversions.

### Challenges I Encountered
* **Referential Integrity & Temporal Consistency Across 176,178 Snapshots:**  
  Maintaining strict chronological alignment across 7 linked tables was complex: ensuring loans only generate payment schedules after origination, payments respect 5-stage waterfalls (penalties $\to$ interest $\to$ principal $\to$ prepayments), and bureau scores update quarterly without forward-looking data leakage or memory bottlenecks.

### What I’m Most Proud Of
* **A Zero-Cost, Production-Grade Financial Simulation:**  
  Building an end-to-end simulation that produces 176,178 high-fidelity financial transactions matching real-world Philippine economic shocks with **PHP 0.00 AI text spend**, complete reproducibility (`SEED = 42`), and full Google Colab & Google Drive compatibility.

### What I Would Improve
* **Loan Modification & Restructuring Modules:**  
  Expand the delinquency module to simulate formal loan restructuring programs (forbearance, tenor extensions, payment holidays) aligned with BSP relief circulars, and introduce spatial geographic correlation to model typhoon-driven localized agricultural and housing default shocks.

---

## Slide 7: Looking Forward

### What I’m Exploring Next
* **Deep Generative Tabular Models & Causal ML:**  
  Building on SD-186, I am investigating Tabular Diffusion Models and Conditional WGANs embedded with structural causal DAG constraints, as well as Doubly Robust estimators and Causal Forests for counterfactual credit decisioning.

### Career Interests and Opportunities
* **Target Roles:**  
  Actively pursuing opportunities in **Quantitative Credit Risk Modeling, Financial Machine Learning, Data Science, and FinTech Analytics** within commercial banking, digital lending platforms, and financial risk consultancies.
* **Value Proposition:**  
  Combining rigorous mathematical modeling, regulatory expertise (IFRS 9 / Basel III), and modern machine learning engineering to deliver high-integrity predictive systems that protect capital and drive sustainable portfolio growth.

### How EIF Helped Prepare Me
* **Holistic Systems & Product Thinking:**  
  The Eskwelabs Innovation Fellowship (Cohort 11 Data Innovation Track) transformed my approach from writing isolated scripts to architecting enterprise-grade data products. It taught me to anchor technical solutions in domain realities, regulatory compliance, and business constraints before writing a single line of machine learning code.

---

## Slide 8: Thank You

```
========================================================================================
                                      Thank You!
========================================================================================

                             Alodivinno Ricco L. Cantos
                      Lead Quantitative Credit Risk Modeler & 
                             Synthetic Data Architect
                 Eskwelabs Innovation Fellowship (EIF) — Cohort 11
                               Data Innovation Track

   * GitHub: https://github.com/l4hgs/sd186-loan-portfolio
   * Project: Synthetic Loan Portfolio Performance Data Model (SD-186)
   * Repository & Notebooks: Fully executed and Colab-ready
========================================================================================
```
