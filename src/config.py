"""
Project SD-186: Loan Portfolio Performance
Configuration and Parameter Register (LOCKED, CALIBRATED, ASSUMED).
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_EXPORT_DIR = DATA_DIR / "raw_export"
DIAGNOSTICS_DIR = DATA_DIR / "diagnostics"
OUTPUTS_DIR = BASE_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
DOCS_DIR = BASE_DIR / "docs"

# Ensure directories exist
for p in [RAW_EXPORT_DIR, DIAGNOSTICS_DIR, FIGURES_DIR, DOCS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# 1. LOCKED GLOBAL PARAMETERS
# ---------------------------------------------------------
SEED: int = 42
CURRENCY: str = "PHP"
DECIMALS: int = 2

# Time Horizon
T_WARMUP: int = 6       # t in [-6, -1] (2022-07 to 2022-12)
T_OBS: int = 36         # t in [0, 35]   (2023-01 to 2025-12)
T_TOTAL: int = T_WARMUP + T_OBS  # 42 monthly snapshots

START_WARMUP_DATE: str = "2022-07-01"
START_OBS_DATE: str = "2023-01-01"
END_OBS_DATE: str = "2025-12-31"

# Macro Shock Window
SHOCK_START_T: int = 10  # Oct 2023
SHOCK_END_T: int = 20    # Aug 2024

# Scale defaults
DEFAULT_N_BORROWERS: int = 6000
SMOKE_TEST_N_BORROWERS: int = 1000

# ---------------------------------------------------------
# 2. CALIBRATED & ASSUMED PRODUCT PARAMETERS
# ---------------------------------------------------------
# Product Mix Weights
PRODUCT_WEIGHTS = {
    "PERSONAL": 0.40,
    "AUTO": 0.25,
    "HOUSING": 0.15,
    "SME_WC": 0.20,
}

# Contract Terms & Underwriting Constraints
PRODUCT_CONFIG = {
    "PERSONAL": {
        "term_months_options": [12, 18, 24, 36],
        "term_weights": [0.25, 0.35, 0.25, 0.15],
        "principal_min": 15_000.0,
        "principal_max": 500_000.0,
        "principal_increment": 1_000.0,
        "apr_min": 0.18,
        "apr_max": 0.36,
        "rate_type": "FIXED",
        "is_secured": False,
        "collateral_type": None,
        "unsec_lgd_a": 8.0,
        "unsec_lgd_b": 2.0,  # Beta(8, 2) mean 80%
        "beta_0": -6.10,      # Calibrated for 8-14% cumulative 90+ DPD
        "smm_gamma_0": -4.20, # SMM full prepayment base logit
        "tau_p": 9.0,        # Seasoning ramp tau
    },
    "AUTO": {
        "term_months_options": [36, 48, 60],
        "term_weights": [0.20, 0.45, 0.35],
        "principal_min": 300_000.0,
        "principal_max": 2_500_000.0,
        "principal_increment": 10_000.0,
        "apr_min": 0.09,
        "apr_max": 0.15,
        "rate_type": "FIXED",
        "is_secured": True,
        "collateral_type": "VEHICLE_CHATTEL",
        "ltv_a": 8.0,
        "ltv_b": 2.0,
        "ltv_min": 0.70,
        "ltv_max": 0.90,
        "drift_min": -0.18,
        "drift_max": -0.10,
        "haircut_a": 4.5,
        "haircut_b": 5.5,    # mean 45%
        "liq_lag_min": 6,
        "liq_lag_max": 10,
        "beta_0": -7.60,      # Calibrated for 2-4% cumulative 90+ DPD
        "smm_gamma_0": -4.50,
        "tau_p": 12.0,
    },
    "HOUSING": {
        "term_months_options": [60, 120, 180, 240],
        "term_weights": [0.15, 0.35, 0.30, 0.20],
        "principal_min": 1_000_000.0,
        "principal_max": 8_000_000.0,
        "principal_increment": 50_000.0,
        "apr_min": 0.065,
        "apr_max": 0.105,
        "rate_type": "FLOATING_ANNUAL",
        "is_secured": True,
        "collateral_type": "RESIDENTIAL_REM",
        "ltv_a": 7.0,
        "ltv_b": 3.0,
        "ltv_min": 0.60,
        "ltv_max": 0.85,
        "drift_min": 0.01,
        "drift_max": 0.05,
        "haircut_a": 3.0,
        "haircut_b": 8.0,    # mean 27.3%
        "liq_lag_min": 12,
        "liq_lag_max": 18,
        "beta_0": -8.50,      # Calibrated for 1-2.5% cumulative 90+ DPD
        "smm_gamma_0": -4.70,
        "tau_p": 18.0,
    },
    "SME_WC": {
        "term_months_options": [12, 24, 36, 48],
        "term_weights": [0.30, 0.35, 0.25, 0.10],
        "principal_min": 100_000.0,
        "principal_max": 5_000_000.0,
        "principal_increment": 10_000.0,
        "apr_min": 0.12,
        "apr_max": 0.22,
        "rate_type": "MIXED", # 50% FIXED, 50% FLOATING_ANNUAL
        "is_secured_prob": 0.70,
        "collateral_type": "SME_EQUIPMENT_REM",
        "ltv_a": 6.0,
        "ltv_b": 4.0,
        "ltv_min": 0.50,
        "ltv_max": 0.80,
        "drift_min": -0.15,
        "drift_max": -0.05,
        "haircut_a": 4.0,
        "haircut_b": 6.0,    # mean 40%
        "liq_lag_min": 6,
        "liq_lag_max": 14,
        "unsec_lgd_a": 7.0,
        "unsec_lgd_b": 3.0,
        "beta_0": -7.10,      # Calibrated for 4-7% cumulative 90+ DPD
        "smm_gamma_0": -4.30,
        "tau_p": 8.0,
    },
}

# ---------------------------------------------------------
# 3. LATENT & BEHAVIORAL PARAMETERS
# ---------------------------------------------------------
# Latent correlation between Cash-Flow Resilience U and Shadow Debt W
RHO_U_W: float = -0.35

# Macro parameters
MACRO_PHI: float = 0.65
MACRO_SHOCK_MAG: float = 0.85
BSP_BASE_RATE: float = 0.055
INFLATION_BASE: float = 0.035
UNEMPLOYMENT_BASE: float = 0.045

# Distress hazard weights (eta_j,t)
BETA_U: float = 0.85
BETA_W: float = 0.75
BETA_DTI: float = 1.40
BETA_MACRO: float = 0.45
BETA_SHOCK: float = 1.20
BETA_DPD: float = 3.20

# Cure probability parameters: P(Cure | DPD > 0)
THETA_0: float = 0.15
THETA_DPD: float = 1.15
THETA_U: float = 0.60
THETA_W: float = 0.40
THETA_MACRO: float = 0.45
THETA_Q4: float = 0.50

# Partial payment probability conditional on distress
P_PARTIAL_BASE: float = 0.40
ALPHA_PART_A: float = 2.5
ALPHA_PART_B: float = 2.5

# Prepayment parameters
GAMMA_RATE: float = 12.0
GAMMA_U: float = 0.35
GAMMA_W: float = 0.30
GAMMA_Q4: float = 0.45  # Q4 bonus windfall

# IFRS 9 Staging thresholds
SICR_RATIO_THRESHOLD: float = 2.0
DPD_STAGE_2: int = 30
DPD_STAGE_3: int = 90
DPD_CHARGE_OFF: int = 180

# Workout fee
WORKOUT_COST_PCT: float = 0.08

# Posting lag distribution (0, 1, 2, 3 days)
POSTING_LAG_WEIGHTS = {0: 0.82, 1: 0.10, 2: 0.05, 3: 0.03}
PAYMENT_REVERSAL_RATE: float = 0.015

# Export tables
EXPORT_TABLES = [
    "Borrowers.csv",
    "CreditScores.csv",
    "Loans.csv",
    "Collateral.csv",
    "RepaymentSchedules.csv",
    "Payments.csv",
    "DelinquencyEvents.csv",
]

# Prohibited columns in exported CSVs
PROHIBITED_EXPORT_COLUMNS = {
    "U_resilience",
    "W_informal_debt",
    "Z_macro_latent",
    "_orig_t",
    "_b_idx",
    "_macro_regime_driver",
    "_regime",
    "_spread",
    "_beta_0",
    "_latent_u",
    "_latent_w",
}
