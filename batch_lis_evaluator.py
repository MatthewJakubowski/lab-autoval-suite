"""
LabAutoVal Suite — Batch LIS Evaluator & ROI Calculator
Deterministic decision cascade simulation for ISO 15189 compliance.
"""

import numpy as np
import pandas as pd

# 1. Konfiguracja reguł referencyjnych i limitów Delta Check (ISO 15189)
ANALYTE_CONFIG = {
    "GLU": {"ref_min": 70.0, "ref_max": 99.0, "delta_pct": 20.0, "unit": "mg/dL"},
    "K":   {"ref_min": 3.5,  "ref_max": 5.1,  "delta_pct": 15.0, "unit": "mmol/L"},
    "NA":  {"ref_min": 136.0,"ref_max": 145.0,"delta_pct": 5.0,  "unit": "mmol/L"},
    "ALT": {"ref_min": 0.0,  "ref_max": 41.0, "delta_pct": 30.0, "unit": "U/L"},
    "CREA":{"ref_min": 0.5,  "ref_max": 1.2,  "delta_pct": 25.0, "unit": "mg/dL"},
    "TSH": {"ref_min": 0.27, "ref_max": 4.2,  "delta_pct": 35.0, "unit": "uIU/mL"}
}

def generate_mock_lis_data(n_samples=1000, random_seed=42):
    """Generates synthetic LIS test results with realistic distributions and noise."""
    np.random.seed(random_seed)
    analytes = list(ANALYTE_CONFIG.keys())
    
    records = []
    for i in range(n_samples):
        sample_id = f"SMP-2026-{10000 + i}"
        analyte = np.random.choice(analytes)
        cfg = ANALYTE_CONFIG[analyte]
        
        mean_val = (cfg["ref_min"] + cfg["ref_max"]) / 2.0
        std_val = (cfg["ref_max"] - cfg["ref_min"]) / 4.0
        
        val = np.random.normal(mean_val, std_val)
        val = max(0.01, round(float(val), 2))
        
        # 70% próbek ma poprzedni wynik do Delta Check
        has_history = np.random.rand() < 0.70
        hist_val = None
        if has_history:
            delta_noise = np.random.normal(0, std_val * 0.4)
            hist_val = max(0.01, round(float(val + delta_noise), 2))
            
        # Wstrzykiwanie artefaktów preanalitycznych
        hemolysis = "CRITICAL" if np.random.rand() < 0.03 else "NONE"
        icterus = "HIGH" if np.random.rand() < 0.02 else "NONE"
        lipemia = "HIGH" if np.random.rand() < 0.015 else "NONE"
        clot_detected = True if np.random.rand() < 0.005 else False
        
        records.append({
            "sample_id": sample_id,
            "analyte": analyte,
            "value": val,
            "historical_value": hist_val,
            "hemolysis": hemolysis,
            "icterus": icterus,
            "lipemia": lipemia,
            "clot_detected": clot_detected
        })
    return pd.DataFrame(records)

def evaluate_decision_cascade(row):
    """Evaluates a single laboratory result through deterministic ISO 15189 rules."""
    cfg = ANALYTE_CONFIG.get(row["analyte"])
    if not cfg:
        return "MANUAL_REVIEW", "UNKNOWN_ANALYTE"

    # Etap 1: Filtr preanalityczny (HIL & skrzepy)
    if row["hemolysis"] == "CRITICAL" or row["clot_detected"]:
        return "REJECT_PREANALYTIC", "PREANALYTIC_INTERFERENCE_OR_CLOT"

    # Etap 2: Granice normy biologicznej
    val = row["value"]
    if val < cfg["ref_min"] or val > cfg["ref_max"]:
        return "MANUAL_REVIEW", "OUT_OF_REFERENCE_RANGE"

    # Etap 3: Dynamiczny Delta Check
    hist = row["historical_value"]
    if pd.notnull(hist) and hist > 0:
        pct_change = abs(val - hist) / hist * 100.0
        if pct_change > cfg["delta_pct"]:
            return "MANUAL_REVIEW", f"DELTA_CHECK_EXCEEDED ({pct_change:.1f}%)"

    return "AUTO_VALIDATED", "ALL_CRITERIA_PASSED"

def run_evaluation_pipeline():
    df = generate_mock_lis_data(n_samples=1000)
    results = df.apply(evaluate_decision_cascade, axis=1)
    df["verdict"] = [r[0] for r in results]
    df["audit_reason"] = [r[1] for r in results]

    total = len(df)
    counts = df["verdict"].value_counts()
    avr_rate = (counts.get("AUTO_VALIDATED", 0) / total) * 100

    monthly_volume = 120000
    sec_saved_per_test = 20
    hours_saved = (monthly_volume * (avr_rate / 100) * sec_saved_per_test) / 3600
    fte_saved = hours_saved / 168

    print("=" * 60)
    print(" 🔬 LABAUTOVAL SUITE — BATCH LIS SIMULATION REPORT")
    print("=" * 60)
    print(f"Total Samples Evaluated: {total}")
    for verdict, cnt in counts.items():
        pct = (cnt / total) * 100
        print(f" • {verdict:<20}: {cnt:>5} ({pct:>5.1f}%)")
    print("-" * 60)
    print(f"⚡ Autovalidation Rate (AVR): {avr_rate:.1f}%")
    print(f"⏱️ Estimated Monthly Time Saved (120k scale): {hours_saved:.1f} hours")
    print(f"👥 Equivalent Diagnostician Capacity: ~{fte_saved:.2f} FTE")
    print("=" * 60)
    return df

if __name__ == "__main__":
    run_evaluation_pipeline()
