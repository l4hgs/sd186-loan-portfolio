"""
Project SD-186: Loan Portfolio Performance
Vectorized Synthetic Data Generators (Stage 0 through Stage 7).
"""

from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy.special import expit

from . import config


# -------------------------------------------------------------
# HELPER DATE UTILITIES
# -------------------------------------------------------------
def get_month_dates(t_warmup: int = config.T_WARMUP, t_obs: int = config.T_OBS) -> List[Tuple[int, pd.Timestamp, pd.Timestamp]]:
    """
    Returns list of (t_idx, start_date, end_date) for t in [-t_warmup, t_obs - 1].
    t = 0 corresponds to 2023-01.
    """
    base_year = 2023
    base_month = 1
    
    month_dates = []
    for t in range(-t_warmup, t_obs):
        # Calculate year and month offset
        total_months = (base_year * 12 + (base_month - 1)) + t
        year = total_months // 12
        month = (total_months % 12) + 1
        
        start_date = pd.Timestamp(year=year, month=month, day=1)
        # End of month
        if month == 12:
            next_start = pd.Timestamp(year=year + 1, month=1, day=1)
        else:
            next_start = pd.Timestamp(year=year, month=month + 1, day=1)
        end_date = next_start - pd.Timedelta(days=1)
        
        month_dates.append((t, start_date, end_date))
        
    return month_dates


# -------------------------------------------------------------
# STAGE 0: MACRO REGIME DRIVER (INTERNAL)
# -------------------------------------------------------------
def generate_macro_series(
    seed: int = config.SEED, 
    t_warmup: int = config.T_WARMUP, 
    t_obs: int = config.T_OBS
) -> pd.DataFrame:
    """
    Generates monthly systemic macroeconomic indicators across [-t_warmup, t_obs - 1].
    Features an AR(1) latent stress index Z_macro with a tightening shock window at t in [10, 20].
    """
    np.random.seed(seed)
    month_dates = get_month_dates(t_warmup, t_obs)
    n_months = len(month_dates)
    
    z_macro = np.zeros(n_months)
    r_bsp = np.zeros(n_months)
    inflation = np.zeros(n_months)
    unemp = np.zeros(n_months)
    
    # Initialize AR(1)
    z_prev = 0.0
    for idx, (t, _, _) in enumerate(month_dates):
        shock = config.MACRO_SHOCK_MAG if (config.SHOCK_START_T <= t <= config.SHOCK_END_T) else 0.0
        eps_z = np.random.normal(0.0, 0.12)
        z_curr = config.MACRO_PHI * z_prev + shock + eps_z
        z_macro[idx] = z_curr
        z_prev = z_curr
        
        # Policy rate, inflation, unemployment
        r_bsp[idx] = np.clip(config.BSP_BASE_RATE + 0.0125 * z_curr + np.random.normal(0, 0.001), 0.020, 0.085)
        inflation[idx] = np.clip(config.INFLATION_BASE + 0.0150 * z_curr + np.random.normal(0, 0.001), 0.015, 0.095)
        unemp[idx] = np.clip(config.UNEMPLOYMENT_BASE + 0.0100 * z_curr + np.random.normal(0, 0.001), 0.030, 0.090)
        
    df_macro = pd.DataFrame({
        "t": [m[0] for m in month_dates],
        "report_month": [m[2].strftime("%Y-%m-%d") for m in month_dates],
        "Z_macro_latent": z_macro,
        "r_BSP": np.round(r_bsp, 4),
        "headline_inflation": np.round(inflation, 4),
        "unemployment_rate": np.round(unemp, 4),
    })
    
    return df_macro


# -------------------------------------------------------------
# STAGE 1: BORROWERS
# -------------------------------------------------------------
def generate_borrowers(n_borrowers: int = config.DEFAULT_N_BORROWERS, seed: int = config.SEED) -> pd.DataFrame:
    """
    Generates static borrower demographics and socioeconomic attributes.
    Generates internal latent traits U_resilience and W_informal_debt.
    """
    np.random.seed(seed)
    
    borrower_ids = [f"BRW-{i+1:06d}" for i in range(n_borrowers)]
    
    # Latent traits
    u_resilience = np.random.normal(0.0, 1.0, n_borrowers)
    eps_w = np.random.normal(0.0, 1.0, n_borrowers)
    w_informal = config.RHO_U_W * u_resilience + np.sqrt(1 - config.RHO_U_W**2) * eps_w
    
    # Age: 21 to 70
    age = np.clip(np.round(np.random.normal(38.0, 10.5, n_borrowers)), 21, 70).astype(int)
    
    # Region code
    regions = ["NCR", "CALABARZON", "CENTRAL_LUZON", "CEBU", "DAVAO", "OTHER_PH"]
    region_probs = [0.40, 0.22, 0.15, 0.10, 0.08, 0.05]
    region_code = np.random.choice(regions, size=n_borrowers, p=region_probs)
    
    # Employment type
    emp_types = ["SALARIED_PRIVATE", "GOVT_EMPLOYEE", "SELF_EMPLOYED_SME", "OFW_REMITTANCE"]
    emp_probs = [0.55, 0.15, 0.20, 0.10]
    emp_type = np.random.choice(emp_types, size=n_borrowers, p=emp_probs)
    
    # Employment tenure months: 3 to 300, with MAR missingness on SELF_EMPLOYED_SME
    tenure_raw = np.clip(np.round(np.random.exponential(48.0, n_borrowers) + 6.0), 3, 300)
    tenure = tenure_raw.astype(float)
    # Inject MAR missingness (~15% of SELF_EMPLOYED_SME)
    sme_mask = (emp_type == "SELF_EMPLOYED_SME")
    sme_nan_mask = sme_mask & (np.random.uniform(0, 1, n_borrowers) < 0.15)
    tenure[sme_nan_mask] = np.nan
    
    # Stated monthly income (PHP): Log-Normal with regional/employment adjustments
    income_base_mu = 10.55  # exp(10.55) approx PHP 38,000
    income_mu = np.full(n_borrowers, income_base_mu)
    income_mu[region_code == "NCR"] += 0.25
    income_mu[region_code == "CALABARZON"] += 0.10
    income_mu[emp_type == "OFW_REMITTANCE"] += 0.30
    income_mu[emp_type == "SELF_EMPLOYED_SME"] += 0.20
    income_mu += 0.15 * u_resilience  # Positive latent resilience slightly boosts earning capacity
    
    stated_income = np.exp(np.random.normal(income_mu, 0.45))
    stated_income = np.clip(np.round(stated_income, 2), 18_000.0, 500_000.0)
    
    # Dependents count (0 to 6)
    dependents = np.clip(np.random.poisson(1.6, n_borrowers), 0, 6)
    
    df_borrowers = pd.DataFrame({
        "borrower_id": borrower_ids,
        "age": age,
        "region_code": region_code,
        "employment_type": emp_type,
        "employment_tenure_months": tenure,
        "stated_monthly_income_php": stated_income,
        "dependents_count": dependents,
        # Latent columns (internal)
        "U_resilience": u_resilience,
        "W_informal_debt": w_informal,
    })
    
    return df_borrowers


# -------------------------------------------------------------
# STAGE 2: CREDIT SCORES (LONGITUDINAL QUARTERLY)
# -------------------------------------------------------------
def generate_credit_scores(
    df_borrowers: pd.DataFrame, 
    df_macro: pd.DataFrame, 
    seed: int = config.SEED
) -> pd.DataFrame:
    """
    Generates quarterly credit bureau score snapshots for each borrower.
    Incorporate MAR missingness (~6.0%), credit utilization, and recent inquiries.
    """
    np.random.seed(seed + 1)
    
    quarter_dates = [
        "2022-09-30", "2022-12-31", 
        "2023-03-31", "2023-06-30", "2023-09-30", "2023-12-31",
        "2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31",
        "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"
    ]
    
    macro_map = df_macro.set_index("report_month")["Z_macro_latent"].to_dict()
    
    n_borrowers = len(df_borrowers)
    records = []
    score_counter = 1
    
    b_ids = df_borrowers["borrower_id"].values
    u_vals = df_borrowers["U_resilience"].values
    w_vals = df_borrowers["W_informal_debt"].values
    incomes = df_borrowers["stated_monthly_income_php"].values
    
    # Pre-generate noise matrices
    for q_date in quarter_dates:
        z_m = macro_map.get(q_date, 0.0)
        eps_s = np.random.normal(0, 32.0, n_borrowers)
        
        # S(i) = clip(round(650 + 55*U(i) - 20*W(i) - 12*Z_macro + eps_s), 300, 850)
        scores_raw = 650.0 + 55.0 * u_vals - 20.0 * w_vals - 12.0 * z_m + eps_s
        scores = np.clip(np.round(scores_raw), 300, 850).astype(float)
        
        # MAR missingness: lower income and high informal debt have higher chance of missing bureau score
        miss_prob = expit(-3.2 - 0.25 * u_vals + 0.30 * w_vals)
        nan_mask = np.random.uniform(0, 1, n_borrowers) < miss_prob  # ~6.0% overall
        
        # Credit utilization: Beta draw increasing with W(i) and macro stress
        util_base = expit(0.15 * w_vals + 0.10 * z_m - 0.20 * u_vals)
        utilization = np.clip(util_base + np.random.normal(0, 0.08, n_borrowers), 0.02, 0.98)
        utilization = np.round(utilization, 4)
        
        # Recent inquiries in 6m (0 to 8)
        inquiries = np.clip(np.random.poisson(1.2 + 0.3 * np.maximum(0, w_vals)), 0, 8).astype(float)
        
        # Apply MAR missingness
        scores[nan_mask] = np.nan
        utilization[nan_mask] = np.nan
        inquiries[nan_mask] = np.nan
        
        for i in range(n_borrowers):
            records.append({
                "score_id": f"SCR-{score_counter:08d}",
                "borrower_id": b_ids[i],
                "quarter_end_date": q_date,
                "bureau_score": scores[i],
                "credit_utilization_ratio": utilization[i],
                "recent_inquiries_6m": inquiries[i],
            })
            score_counter += 1
            
    df_scores = pd.DataFrame(records)
    return df_scores


# -------------------------------------------------------------
# STAGE 3: LOANS
# -------------------------------------------------------------
def generate_loans(
    df_borrowers: pd.DataFrame, 
    seed: int = config.SEED, 
    t_warmup: int = config.T_WARMUP, 
    t_obs: int = config.T_OBS
) -> pd.DataFrame:
    """
    Generates loan contracts across warm-up and observation cohorts.
    Borrowers can hold multiple loans (~1.65 loans/borrower on average).
    """
    np.random.seed(seed + 2)
    month_dates = get_month_dates(t_warmup, t_obs)
    
    n_borrowers = len(df_borrowers)
    # Distribution of loan count per borrower: 1 (50%), 2 (35%), 3 (15%)
    num_loans_per_borrower = np.random.choice([1, 2, 3], size=n_borrowers, p=[0.50, 0.35, 0.15])
    
    products = list(config.PRODUCT_WEIGHTS.keys())
    prod_probs = list(config.PRODUCT_WEIGHTS.values())
    
    loan_records = []
    loan_id_counter = 1
    
    # Origination t_orig range: [-6, 34]
    all_t_values = [m[0] for m in month_dates[:-1]]  # exclude last month for origination
    # Weigh warm-up cohorts slightly higher to establish a seasoned baseline portfolio at t=0
    t_weights = np.ones(len(all_t_values))
    t_weights[:t_warmup] *= 2.2  # Seasoned book weight
    t_weights /= t_weights.sum()
    
    borrower_ids = df_borrowers["borrower_id"].values
    u_vals = df_borrowers["U_resilience"].values
    w_vals = df_borrowers["W_informal_debt"].values
    incomes = df_borrowers["stated_monthly_income_php"].values
    emp_types = df_borrowers["employment_type"].values
    
    for i in range(n_borrowers):
        n_l = num_loans_per_borrower[i]
        b_id = borrower_ids[i]
        u_i = u_vals[i]
        w_i = w_vals[i]
        inc_i = incomes[i]
        emp_i = emp_types[i]
        
        for l_idx in range(n_l):
            # Sample product
            # If SME, boost SME_WC probability
            if emp_i == "SELF_EMPLOYED_SME" and l_idx == 0:
                prod = np.random.choice(products, p=[0.20, 0.15, 0.10, 0.55])
            else:
                prod = np.random.choice(products, p=prod_probs)
                
            p_cfg = config.PRODUCT_CONFIG[prod]
            
            # Origination month
            t_orig = int(np.random.choice(all_t_values, p=t_weights))
            # Find date string for origination
            m_info = [m for m in month_dates if m[0] == t_orig][0]
            orig_date = m_info[1].strftime("%Y-%m-%d")
            
            # Term
            term = int(np.random.choice(p_cfg["term_months_options"], p=p_cfg["term_weights"]))
            
            # Principal: snapped to increment
            inc_bracket = min(inc_i * 12.0, p_cfg["principal_max"])
            raw_p = np.random.uniform(p_cfg["principal_min"], max(p_cfg["principal_min"] + 10_000, inc_bracket))
            increment = p_cfg["principal_increment"]
            principal = float(np.round(raw_p / increment) * increment)
            principal = float(np.clip(principal, p_cfg["principal_min"], p_cfg["principal_max"]))
            
            # APR: within product range, scaled down slightly for positive resilience
            apr_base = (p_cfg["apr_min"] + p_cfg["apr_max"]) / 2.0
            apr_noise = np.random.uniform(-0.02, 0.02) - 0.015 * u_i + 0.010 * w_i
            initial_apr = float(np.clip(apr_base + apr_noise, p_cfg["apr_min"], p_cfg["apr_max"]))
            initial_apr = round(initial_apr, 4)
            
            # Rate type
            if prod == "PERSONAL" or prod == "AUTO":
                rate_type = "FIXED"
            elif prod == "HOUSING":
                rate_type = "FLOATING_ANNUAL"
            else:  # SME_WC
                rate_type = np.random.choice(["FIXED", "FLOATING_ANNUAL"], p=[0.50, 0.50])
                
            # Secured status
            if prod == "PERSONAL":
                is_sec = False
            elif prod in ["AUTO", "HOUSING"]:
                is_sec = True
            else:
                is_sec = bool(np.random.uniform(0, 1) < p_cfg["is_secured_prob"])
                
            loan_records.append({
                "loan_id": f"LN-{loan_id_counter:06d}",
                "borrower_id": b_id,
                "product_type": prod,
                "origination_date": orig_date,
                "term_months": term,
                "principal_php": principal,
                "initial_apr": initial_apr,
                "rate_type": rate_type,
                "is_secured": is_sec,
                # Internal simulation helper
                "_orig_t": t_orig,
                "_b_idx": i,
            })
            loan_id_counter += 1
            
    df_loans = pd.DataFrame(loan_records)
    return df_loans


# -------------------------------------------------------------
# STAGE 4: COLLATERAL
# -------------------------------------------------------------
def generate_collateral(df_loans: pd.DataFrame, seed: int = config.SEED) -> pd.DataFrame:
    """
    Generates collateral asset records for all secured facilities.
    """
    np.random.seed(seed + 3)
    
    secured_loans = df_loans[df_loans["is_secured"]].copy()
    col_records = []
    col_counter = 1
    
    for _, loan in secured_loans.iterrows():
        prod = loan["product_type"]
        p_cfg = config.PRODUCT_CONFIG[prod]
        principal = loan["principal_php"]
        
        col_type = p_cfg["collateral_type"]
        
        # Origination LTV
        ltv = np.random.beta(p_cfg["ltv_a"], p_cfg["ltv_b"])
        orig_ltv = float(np.clip(p_cfg["ltv_min"] + ltv * (p_cfg["ltv_max"] - p_cfg["ltv_min"]), 0.50, 0.90))
        orig_ltv = round(orig_ltv, 4)
        
        # Appraised value
        appraised_val = float(np.round(principal / orig_ltv, 2))
        
        # Value drift rate
        drift = float(np.random.uniform(p_cfg["drift_min"], p_cfg["drift_max"]))
        drift = round(drift, 4)
        
        # Haircut rate (Beta + rare extreme damage outlier up to 80%)
        is_damage_outlier = (np.random.uniform(0, 1) < 0.02)
        if is_damage_outlier:
            haircut = float(np.random.uniform(0.65, 0.80))
        else:
            raw_h = np.random.beta(p_cfg["haircut_a"], p_cfg["haircut_b"])
            haircut = float(np.clip(raw_h, 0.15, 0.65))
        haircut = round(haircut, 4)
        
        # Liquidation lag months
        liq_lag = int(np.random.randint(p_cfg["liq_lag_min"], p_cfg["liq_lag_max"] + 1))
        
        col_records.append({
            "collateral_id": f"COL-{col_counter:06d}",
            "loan_id": loan["loan_id"],
            "collateral_type": col_type,
            "initial_appraised_value_php": appraised_val,
            "origination_ltv": orig_ltv,
            "annual_value_drift_rate": drift,
            "expected_haircut_rate": haircut,
            "expected_liquidation_months": liq_lag,
        })
        col_counter += 1
        
    df_collateral = pd.DataFrame(col_records)
    return df_collateral


# -------------------------------------------------------------
# STAGE 5, 6, 7: SERVICING & CASH FLOWS SIMULATOR
# -------------------------------------------------------------
def simulate_servicing_and_cashflows(
    df_borrowers: pd.DataFrame,
    df_loans: pd.DataFrame,
    df_collateral: pd.DataFrame,
    df_macro: pd.DataFrame,
    seed: int = config.SEED,
    t_warmup: int = config.T_WARMUP,
    t_obs: int = config.T_OBS,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Simulates monthly loan balances, interest accruals, delinquency roll rates,
    IFRS 9 impairment staging, transaction payments, and workout events across [-t_warmup, t_obs - 1].
    Exports only t >= 0 records for RepaymentSchedules and Payments.
    """
    np.random.seed(seed + 4)
    month_dates = get_month_dates(t_warmup, t_obs)
    
    # Pre-index lookups
    borrower_map = df_borrowers.set_index("borrower_id").to_dict(orient="index")
    macro_map = df_macro.set_index("t").to_dict(orient="index")
    col_map = df_collateral.set_index("loan_id").to_dict(orient="index") if len(df_collateral) > 0 else {}
    
    # Prepare loan state tracking
    n_loans = len(df_loans)
    loans_list = df_loans.to_dict(orient="records")
    
    # State vectors for each loan
    balance = np.zeros(n_loans, dtype=float)
    dpd = np.zeros(n_loans, dtype=int)
    arrears = np.zeros(n_loans, dtype=float)
    effective_apr = np.zeros(n_loans, dtype=float)
    status = np.array(["PENDING"] * n_loans, dtype=object)
    
    # Tracking counters
    months_in_default = np.zeros(n_loans, dtype=int)
    pd_12m_orig = np.zeros(n_loans, dtype=float)
    default_date_log = [None] * n_loans
    charge_off_date_log = [None] * n_loans
    ead_at_default_log = [np.nan] * n_loans
    delinquency_event_open = [None] * n_loans  # stores event dict if active
    
    # Spread for floating loans
    base_r_bsp_0 = macro_map[0]["r_BSP"]
    spreads = np.zeros(n_loans, dtype=float)
    for i, l in enumerate(loans_list):
        spreads[i] = max(0.01, l["initial_apr"] - base_r_bsp_0)
        
    schedules_records = []
    payments_records = []
    delinquency_events = []
    
    sched_counter = 1
    pay_counter = 1
    evt_counter = 1
    
    posting_delays = list(config.POSTING_LAG_WEIGHTS.keys())
    posting_probs = list(config.POSTING_LAG_WEIGHTS.values())
    
    for t_idx, start_date, end_date in month_dates:
        report_month_str = end_date.strftime("%Y-%m-%d")
        due_date_str = (start_date + pd.Timedelta(days=14)).strftime("%Y-%m-%d")
        
        m_info = macro_map[t_idx]
        z_macro_t = m_info["Z_macro_latent"]
        r_bsp_t = m_info["r_BSP"]
        pi_t = m_info["headline_inflation"]
        is_q4 = (end_date.month in [11, 12])
        
        for i, loan in enumerate(loans_list):
            t_orig = loan["_orig_t"]
            
            # If loan not originated yet, skip
            if t_idx < t_orig:
                continue
                
            # If loan was already charged off or paid off in prior month, skip
            if status[i] in ["PAID_OFF", "PREPAID", "CHARGED_OFF"]:
                continue
                
            mob = t_idx - t_orig
            term = loan["term_months"]
            rem_term = max(0, term - mob)
            b_id = loan["borrower_id"]
            b_info = borrower_map[b_id]
            u_i = b_info["U_resilience"]
            w_i = b_info["W_informal_debt"]
            income_i = b_info["stated_monthly_income_php"]
            prod = loan["product_type"]
            p_cfg = config.PRODUCT_CONFIG[prod]
            
            # 1. Initialization at origination (MOB == 0)
            if mob == 0:
                balance[i] = loan["principal_php"]
                dpd[i] = 0
                arrears[i] = 0.0
                effective_apr[i] = loan["initial_apr"]
                status[i] = "ACTIVE"
                months_in_default[i] = 0
                
                # Base installment at origination
                r_m0 = loan["initial_apr"] / 12.0
                t_orig_amort = term
                if r_m0 > 0:
                    f0_init = (1.0 + r_m0) ** t_orig_amort
                    m_0_init = loan["principal_php"] * (r_m0 * f0_init) / (f0_init - 1.0)
                else:
                    m_0_init = loan["principal_php"] / t_orig_amort
                dti_0 = float(np.clip((m_0_init + max(0, w_i) * 0.08 * income_i) / max(1.0, income_i), 0.05, 1.25))
                
                # Base hazard at origination
                h_obs_0 = expit(
                    -4.4
                    - 0.40 * u_i
                    + 0.70 * dti_0
                )
                pd_12m_orig[i] = float(np.clip(1.0 - (1.0 - h_obs_0) ** 12, 0.005, 1.0))
                
            # 2. Rate repricing for FLOATING_ANNUAL
            if loan["rate_type"] == "FLOATING_ANNUAL" and mob > 0 and (mob % 12 == 0):
                new_apr = np.clip(r_bsp_t + spreads[i], p_cfg["apr_min"], p_cfg["apr_max"])
                effective_apr[i] = round(float(new_apr), 4)
                
            apr_t = effective_apr[i]
            r_m = apr_t / 12.0
            
            # 3. Monthly scheduled installment M(j, t)
            # Level-payment formula on remaining principal and remaining term
            t_amort = max(1, rem_term)
            if r_m > 0:
                factor = (1.0 + r_m) ** t_amort
                m_jt = balance[i] * (r_m * factor) / (factor - 1.0)
            else:
                m_jt = balance[i] / t_amort
            m_jt = float(np.round(m_jt, 2))
            
            # Initial installment benchmark for rate shock calculation
            t_orig_amort = term
            if r_m > 0:
                f0 = (1.0 + (loan["initial_apr"]/12.0)) ** t_orig_amort
                m_0 = loan["principal_php"] * ((loan["initial_apr"]/12.0) * f0) / (f0 - 1.0)
            else:
                m_0 = loan["principal_php"] / t_orig_amort
            m_0 = max(1.0, float(m_0))
            
            # Monthly accrued interest
            accrued_interest = float(np.round(balance[i] * r_m, 2))
            
            # 4. Latent Distress & Payment Mechanics
            # Dynamic DTI
            real_income = income_i * (1.0 - 0.40 * pi_t)
            dti = float(np.clip((m_jt + max(0, w_i) * 0.08 * income_i) / max(1.0, real_income), 0.05, 1.25))
            
            rate_shock = max(0.0, (m_jt - m_0) / m_0)
            prior_delinq_indicator = 1.0 if dpd[i] > 0 else 0.0
            
            # eta_j,t
            eps_eta = np.random.normal(0.0, 0.95)
            eta = (
                p_cfg["beta_0"]
                - config.BETA_U * u_i
                + config.BETA_W * w_i
                + config.BETA_DTI * dti
                + config.BETA_MACRO * z_macro_t
                + config.BETA_SHOCK * rate_shock
                + config.BETA_DPD * prior_delinq_indicator
                + eps_eta
            )
            p_distress = float(expit(eta))
            
            # Payment outcome branches
            amount_paid = 0.0
            applied_fees = 0.0
            applied_interest = 0.0
            applied_principal = 0.0
            payment_type = "SCHEDULED"
            is_reversed = False
            
            prev_dpd = dpd[i]
            
            # --- BRANCH A: Currently Performing (DPD == 0) ---
            if prev_dpd == 0:
                # Prepayment hazard SMM
                delta_r = max(0.0, apr_t - (r_bsp_t + spreads[i]))
                seasoning_ramp = 1.0 - np.exp(-max(0.0, mob - 3) / p_cfg["tau_p"])
                smm_logit = (
                    p_cfg["smm_gamma_0"]
                    + config.GAMMA_RATE * delta_r
                    + config.GAMMA_U * u_i
                    - config.GAMMA_W * w_i
                    + (config.GAMMA_Q4 if is_q4 else 0.0)
                )
                smm_hazard = float(expit(smm_logit) * seasoning_ramp)
                
                # Check Full Prepayment
                is_full_prepay = (np.random.uniform(0, 1) < smm_hazard)
                
                if is_full_prepay:
                    payment_type = "FULL_PREPAYMENT"
                    applied_interest = accrued_interest
                    applied_principal = balance[i]
                    amount_paid = float(np.round(applied_interest + applied_principal, 2))
                    balance[i] = 0.0
                    status[i] = "PREPAID"
                    dpd[i] = 0
                else:
                    # Check payment distress
                    is_distressed = (np.random.uniform(0, 1) < p_distress)
                    if not is_distressed:
                        # Full scheduled payment
                        payment_type = "SCHEDULED"
                        # Check partial curtailment if U > 0
                        curtailment = 0.0
                        if u_i > 0 and (np.random.uniform(0, 1) < 0.04):
                            curtailment = float(np.round(np.random.uniform(0.5, 2.0) * m_jt, 2))
                            payment_type = "CURTAILMENT"
                            
                        # Waterfall: interest first, then principal
                        applied_interest = min(accrued_interest, m_jt)
                        sched_p = max(0.0, m_jt - applied_interest)
                        applied_principal = min(balance[i], sched_p + curtailment)
                        amount_paid = float(np.round(applied_interest + applied_principal, 2))
                        balance[i] = max(0.0, balance[i] - applied_principal)
                        dpd[i] = 0
                        arrears[i] = 0.0
                        
                        if balance[i] <= 0.01 or rem_term <= 0:
                            balance[i] = 0.0
                            status[i] = "PAID_OFF"
                        else:
                            status[i] = "ACTIVE"
                    else:
                        # Distressed: partial or miss
                        status[i] = "DELINQUENT"
                        dpd[i] = 30
                        # Check partial payment
                        if np.random.uniform(0, 1) < config.P_PARTIAL_BASE:
                            payment_type = "PARTIAL"
                            alpha_part = float(np.random.beta(config.ALPHA_PART_A, config.ALPHA_PART_B))
                            amount_paid = float(np.round(alpha_part * m_jt, 2))
                            applied_interest = min(accrued_interest, amount_paid)
                            applied_principal = max(0.0, min(balance[i], amount_paid - applied_interest))
                            balance[i] = max(0.0, balance[i] - applied_principal)
                            unpaid_part = max(0.0, m_jt - amount_paid)
                            arrears[i] += unpaid_part
                        else:
                            # Complete miss
                            amount_paid = 0.0
                            applied_interest = 0.0
                            applied_principal = 0.0
                            arrears[i] += m_jt
                            
                        # Open a DelinquencyEvent if none active
                        if delinquency_event_open[i] is None:
                            delinquency_event_open[i] = {
                                "event_id": f"EVT-{evt_counter:06d}",
                                "loan_id": loan["loan_id"],
                                "episode_start_month": report_month_str,
                                "default_90dpd_date": None,
                                "charge_off_date": None,
                                "ead_at_default_php": np.nan,
                                "gross_recovery_php": np.nan,
                                "workout_cost_php": np.nan,
                                "net_recovery_php": np.nan,
                                "recovery_lag_months": np.nan,
                                "realized_lgd": np.nan,
                                "resolution_status": "ACTIVE_DEFAULT",
                            }
                            evt_counter += 1

            # --- BRANCH B: Delinquent / Default in Prior Month (prev_dpd > 0) ---
            else:
                # Cure probability
                dpd_bucket_idx = prev_dpd / 30.0
                cure_logit = (
                    config.THETA_0
                    - config.THETA_DPD * dpd_bucket_idx
                    + config.THETA_U * u_i
                    - config.THETA_W * w_i
                    - config.THETA_MACRO * z_macro_t
                    + (config.THETA_Q4 if is_q4 else 0.0)
                )
                p_cure = float(expit(cure_logit))
                
                is_cure = (np.random.uniform(0, 1) < p_cure)
                
                if is_cure:
                    payment_type = "CURE"
                    # Borrower cures: pays scheduled + accrued interest + arrears
                    applied_interest = accrued_interest
                    applied_principal = min(balance[i], m_jt + arrears[i])
                    amount_paid = float(np.round(applied_interest + applied_principal, 2))
                    balance[i] = max(0.0, balance[i] - applied_principal)
                    dpd[i] = 0
                    arrears[i] = 0.0
                    months_in_default[i] = 0
                    
                    if balance[i] <= 0.01:
                        balance[i] = 0.0
                        status[i] = "PAID_OFF"
                    else:
                        status[i] = "ACTIVE"
                        
                    # Close delinquency event as CURED
                    if delinquency_event_open[i] is not None:
                        delinquency_event_open[i]["resolution_status"] = "CURED"
                        delinquency_events.append(delinquency_event_open[i])
                        delinquency_event_open[i] = None
                        
                else:
                    # Did not cure. Check if makes scheduled or partial or misses
                    is_distressed = (np.random.uniform(0, 1) < p_distress)
                    if not is_distressed:
                        # Keeps current bucket, pays current scheduled installment
                        payment_type = "SCHEDULED"
                        applied_interest = min(accrued_interest, m_jt)
                        sched_p = max(0.0, m_jt - applied_interest)
                        applied_principal = min(balance[i], sched_p)
                        amount_paid = float(np.round(applied_interest + applied_principal, 2))
                        balance[i] = max(0.0, balance[i] - applied_principal)
                        # DPD stays unchanged (rolls in place)
                        dpd[i] = prev_dpd
                    else:
                        # Distressed: advances DPD by +30
                        dpd[i] = prev_dpd + 30
                        if np.random.uniform(0, 1) < config.P_PARTIAL_BASE:
                            payment_type = "PARTIAL"
                            alpha_part = float(np.random.beta(config.ALPHA_PART_A, config.ALPHA_PART_B))
                            amount_paid = float(np.round(alpha_part * m_jt, 2))
                            applied_interest = min(accrued_interest, amount_paid)
                            applied_principal = max(0.0, min(balance[i], amount_paid - applied_interest))
                            balance[i] = max(0.0, balance[i] - applied_principal)
                            arrears[i] += max(0.0, m_jt - amount_paid)
                        else:
                            # Complete miss
                            amount_paid = 0.0
                            applied_interest = 0.0
                            applied_principal = 0.0
                            arrears[i] += m_jt
                            
                    # Update status for default / charge-off
                    if dpd[i] >= 90:
                        status[i] = "DEFAULT_90P"
                        months_in_default[i] += 1
                        
                        # First time hitting 90 DPD
                        if default_date_log[i] is None:
                            default_date_log[i] = report_month_str
                            ead_at_default_log[i] = float(np.round(balance[i] + accrued_interest, 2))
                            if delinquency_event_open[i] is not None:
                                delinquency_event_open[i]["default_90dpd_date"] = report_month_str
                                delinquency_event_open[i]["ead_at_default_php"] = ead_at_default_log[i]
                                delinquency_event_open[i]["resolution_status"] = "ACTIVE_DEFAULT"
                                
                        # Check Charge-off absorbing state (3 consecutive months in 90+ DPD -> DPD >= 180)
                        if dpd[i] >= config.DPD_CHARGE_OFF:
                            status[i] = "CHARGED_OFF"
                            charge_off_date_log[i] = report_month_str
                            
                            # Finalize recovery calculation for the charged off loan
                            ead_def = ead_at_default_log[i] if not np.isnan(ead_at_default_log[i]) else (balance[i] + accrued_interest)
                            
                            if loan["is_secured"] and loan["loan_id"] in col_map:
                                c_info = col_map[loan["loan_id"]]
                                v_init = c_info["initial_appraised_value_php"]
                                drift = c_info["annual_value_drift_rate"]
                                h_rate = c_info["expected_haircut_rate"]
                                liq_lag = c_info["expected_liquidation_months"]
                                
                                # Value at default with drift
                                v_def = v_init * ((1.0 + drift) ** (mob / 12.0))
                                gross_rec = min(ead_def, v_def * (1.0 - h_rate))
                                workout_fee = gross_rec * config.WORKOUT_COST_PCT
                                net_rec = max(0.0, gross_rec - workout_fee)
                                disc_factor = (1.0 + apr_t / 12.0) ** liq_lag
                                realized_lgd = float(np.clip(1.0 - (net_rec / (max(1.0, ead_def) * disc_factor)), 0.05, 0.98))
                            else:
                                # Unsecured recovery
                                liq_lag = int(np.random.randint(6, 12))
                                unsec_lgd = float(np.random.beta(p_cfg["unsec_lgd_a"], p_cfg["unsec_lgd_b"]))
                                gross_rec = float(np.round(ead_def * (1.0 - unsec_lgd), 2))
                                workout_fee = float(np.round(gross_rec * config.WORKOUT_COST_PCT, 2))
                                net_rec = max(0.0, gross_rec - workout_fee)
                                disc_factor = (1.0 + apr_t / 12.0) ** liq_lag
                                realized_lgd = float(np.clip(1.0 - (net_rec / (max(1.0, ead_def) * disc_factor)), 0.05, 0.98))
                                
                            if delinquency_event_open[i] is not None:
                                delinquency_event_open[i]["charge_off_date"] = report_month_str
                                delinquency_event_open[i]["gross_recovery_php"] = round(gross_rec, 2)
                                delinquency_event_open[i]["workout_cost_php"] = round(workout_fee, 2)
                                delinquency_event_open[i]["net_recovery_php"] = round(net_rec, 2)
                                delinquency_event_open[i]["recovery_lag_months"] = liq_lag
                                delinquency_event_open[i]["realized_lgd"] = round(realized_lgd, 4)
                                delinquency_event_open[i]["resolution_status"] = "CHARGED_OFF_SETTLED"
                                delinquency_events.append(delinquency_event_open[i])
                                delinquency_event_open[i] = None
                                
                            # Absorbing state: balance sets to 0 for active servicing
                            balance[i] = 0.0
                    else:
                        status[i] = "DELINQUENT"
                        
            # 5. IFRS 9 Staging & Forward-looking ECL
            # Observable hazard h_obs with macro sensitivity heterogeneous across vulnerability
            macro_vuln = 0.05 + 0.25 * max(0.0, -u_i) + 0.16 * max(0.0, w_i)
            h_obs = expit(
                -4.4
                - 0.40 * (u_i + np.random.normal(0, 0.15))
                + 0.70 * dti
                + macro_vuln * z_macro_t
                + 1.80 * (1.0 if dpd[i] > 0 else 0.0)
            )
            pd_12m_val = float(np.clip(1.0 - (1.0 - h_obs) ** 12, 0.0001, 1.0))
            pd_lt_val = float(np.clip(1.0 - (1.0 - h_obs) ** max(12, min(term, 60)), 0.0001, 1.0))
            
            # Staging
            if dpd[i] >= 90 or status[i] == "CHARGED_OFF":
                ifrs9_stage = "STAGE_3"
                pd_calc = 1.0
                pd_12m_val = 1.0
            elif dpd[i] >= config.DPD_STAGE_2:
                ifrs9_stage = "STAGE_2"
                pd_calc = pd_lt_val
            else:
                # Check SICR ratio: compare against origination baseline hazard
                base_pd = pd_12m_orig[i] if pd_12m_orig[i] > 0 else 0.02
                sicr_ratio = pd_12m_val / base_pd
                if sicr_ratio >= config.SICR_RATIO_THRESHOLD:
                    ifrs9_stage = "STAGE_2"
                    pd_calc = pd_lt_val
                else:
                    ifrs9_stage = "STAGE_1"
                    pd_calc = pd_12m_val
                    
            ead_val = float(np.round(balance[i] + accrued_interest, 2))
            
            # Point-in-time LGD
            if loan["is_secured"] and loan["loan_id"] in col_map:
                c_info = col_map[loan["loan_id"]]
                lgd_pit = float(np.clip(c_info["expected_haircut_rate"] + 0.10, 0.05, 0.90))
            else:
                lgd_pit = 0.80
                
            ecl_reserve = float(np.round(pd_calc * lgd_pit * ead_val, 2)) if status[i] not in ["PAID_OFF", "PREPAID", "CHARGED_OFF"] else 0.0
            
            # 6. Record Schedule and Payment (Filtered to t >= 0 for export)
            sched_id = f"SCH-{sched_counter:08d}"
            sched_counter += 1
            
            # Add to schedule list if in observation window (t >= 0)
            if t_idx >= 0:
                schedules_records.append({
                    "schedule_id": sched_id,
                    "loan_id": loan["loan_id"],
                    "report_month": report_month_str,
                    "mob": mob,
                    "remaining_term_months": rem_term,
                    "effective_apr": apr_t,
                    "scheduled_installment_php": m_jt,
                    "ending_balance_php": round(balance[i], 2),
                    "accrued_interest_php": round(accrued_interest, 2),
                    "arrears_balance_php": round(arrears[i], 2),
                    "dpd": int(dpd[i]),
                    "ifrs9_stage": ifrs9_stage,
                    "pd_12m": round(pd_12m_val, 4),
                    "lgd": round(lgd_pit, 4),
                    "ead_php": ead_val,
                    "ecl_reserve_php": ecl_reserve,
                    "loan_status": status[i],
                })
                
                # Payment transaction (if payment made or recorded)
                if amount_paid > 0 or payment_type in ["SCHEDULED", "PARTIAL", "FULL_PREPAYMENT", "CURE", "CURTAILMENT"]:
                    # Interbank posting delay
                    lag_days = int(np.random.choice(posting_delays, p=posting_probs))
                    posting_date = (pd.Timestamp(due_date_str) + pd.Timedelta(days=lag_days)).strftime("%Y-%m-%d")
                    
                    # Reversal noise (~1.5%)
                    is_rev = bool(np.random.uniform(0, 1) < config.PAYMENT_REVERSAL_RATE)
                    
                    payments_records.append({
                        "payment_id": f"PAY-{pay_counter:08d}",
                        "loan_id": loan["loan_id"],
                        "schedule_id": sched_id,
                        "due_date": due_date_str,
                        "posting_date": posting_date,
                        "payment_type": payment_type,
                        "amount_paid_php": amount_paid,
                        "applied_principal_php": round(applied_principal, 2),
                        "applied_interest_php": round(applied_interest, 2),
                        "applied_fees_php": applied_fees,
                        "is_reversed": is_rev,
                    })
                    pay_counter += 1
                    
    # Append any remaining open delinquency events that didn't cure or charge off
    for evt in delinquency_event_open:
        if evt is not None:
            delinquency_events.append(evt)
            
    df_schedules = pd.DataFrame(schedules_records)
    df_payments = pd.DataFrame(payments_records)
    df_delinquency = pd.DataFrame(delinquency_events)
    
    return df_schedules, df_payments, df_delinquency


# -------------------------------------------------------------
# HIGH-LEVEL DAG ORCHESTRATOR
# -------------------------------------------------------------
def run_full_pipeline(
    n_borrowers: int = config.DEFAULT_N_BORROWERS, 
    seed: int = config.SEED, 
    t_warmup: int = config.T_WARMUP, 
    t_obs: int = config.T_OBS
) -> Dict[str, pd.DataFrame]:
    """
    Executes the complete synthetic data generation pipeline across Stage 0 to Stage 7.
    Returns a dictionary of all 7 catalog tables plus internal macro series.
    """
    print(f"Executing DAG pipeline with N_BORROWERS={n_borrowers}, SEED={seed}, WARMUP={t_warmup}, OBS={t_obs}...")
    
    # Stage 0: Macro driver
    df_macro = generate_macro_series(seed=seed, t_warmup=t_warmup, t_obs=t_obs)
    
    # Stage 1: Borrowers
    df_borrowers = generate_borrowers(n_borrowers=n_borrowers, seed=seed)
    
    # Stage 2: CreditScores
    df_credit_scores = generate_credit_scores(df_borrowers=df_borrowers, df_macro=df_macro, seed=seed)
    
    # Stage 3: Loans
    df_loans = generate_loans(df_borrowers=df_borrowers, seed=seed, t_warmup=t_warmup, t_obs=t_obs)
    
    # Stage 4: Collateral
    df_collateral = generate_collateral(df_loans=df_loans, seed=seed)
    
    # Stage 5, 6, 7: Monthly servicing & cash flows simulation
    df_schedules, df_payments, df_delinquency = simulate_servicing_and_cashflows(
        df_borrowers=df_borrowers,
        df_loans=df_loans,
        df_collateral=df_collateral,
        df_macro=df_macro,
        seed=seed,
        t_warmup=t_warmup,
        t_obs=t_obs,
    )
    
    tables = {
        "_macro_regime_driver": df_macro,
        "Borrowers": df_borrowers,
        "CreditScores": df_credit_scores,
        "Loans": df_loans,
        "Collateral": df_collateral,
        "RepaymentSchedules": df_schedules,
        "Payments": df_payments,
        "DelinquencyEvents": df_delinquency,
    }
    
    print("Pipeline generation completed successfully.")
    return tables
