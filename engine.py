"""
LabAutoVal Decision Engine - Core Architecture
Explainable autovalidation & delta check simulator for clinical laboratories.
ISO 15189 Aligned | Proof of Concept
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import numpy as np
import pandas as pd


class DecisionVerdict(str, Enum):
    AUTO_VALIDATED = "AUTO_VALIDATED"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    REJECT_PREANALYTIC = "REJECT_PREANALYTIC"


@dataclass
class AnalyteConfig:
    code: str
    name: str
    unit: str
    min_val: float
    max_val: float
    delta_limit_pct: float
    pop_mean: float
    pop_sd: float


CONFIG_REGISTRY: Dict[str, AnalyteConfig] = {
    "GLU": AnalyteConfig("GLU", "Glucose", "mg/dl", 70.0, 99.0, 25.0, 89.0, 13.0),
    "K": AnalyteConfig("K", "Potassium", "mmol/l", 3.5, 5.1, 15.0, 4.3, 0.45),
    "NA": AnalyteConfig("NA", "Sodium", "mmol/l", 136.0, 145.0, 10.0, 140.5, 3.2),
    "ALT": AnalyteConfig("ALT", "Alanine Aminotransferase", "U/l", 0.0, 41.0, 50.0, 25.0, 15.0),
    "CREA": AnalyteConfig("CREA", "Creatinine", "mg/dl", 0.6, 1.2, 20.0, 0.88, 0.22),
    "TSH": AnalyteConfig("TSH", "Thyrotropin", "µIU/ml", 0.27, 4.2, 40.0, 2.1, 1.1),
}


class LabDecisionEngine:
    def __init__(self, config: Optional[Dict[str, AnalyteConfig]] = None):
        self.registry = config or CONFIG_REGISTRY

    def evaluate_sample(
        self,
        analyte: str,
        current_val: float,
        previous_val: Optional[float] = None,
        hemolysis: bool = False,
        lipemia: bool = False,
        clot_alert: bool = False,
    ) -> Dict[str, Any]:
        """
        Evaluates a single sample through deterministic rule cascade (XAI trace).
        """
        if analyte not in self.registry:
            raise ValueError(f"Unknown analyte: {analyte}")

        cfg = self.registry[analyte]
        trace = []

        # Step 1: Preanalytical & Hardware Flags
        flags_pass = not (hemolysis or clot_alert)
        trace.append({
            "step": 1,
            "name": "Hardware & Preanalytics (HIL/Clot)",
            "passed": flags_pass,
            "details": f"Hemo={hemolysis}, Lip={lipemia}, Clot={clot_alert}"
        })

        if clot_alert or hemolysis:
            return {
                "verdict": DecisionVerdict.REJECT_PREANALYTIC,
                "reason": "Hardware clot alert or critical hemolysis index triggered.",
                "trace": trace,
            }

        # Step 2: Reference Interval Check
        range_pass = cfg.min_val <= current_val <= cfg.max_val
        trace.append({
            "step": 2,
            "name": f"Reference Interval ({cfg.min_val}-{cfg.max_val} {cfg.unit})",
            "passed": range_pass,
            "details": f"Measured: {current_val} {cfg.unit}"
        })

        # Step 3: Dynamic Delta Check
        delta_pass = True
        delta_pct = 0.0
        if previous_val is not None and previous_val > 0:
            delta_pct = abs(current_val - previous_val) / previous_val * 100.0
            if delta_pct > cfg.delta_limit_pct:
                delta_pass = False

        trace.append({
            "step": 3,
            "name": f"Dynamic Delta Check (Max: {cfg.delta_limit_pct}%)",
            "passed": delta_pass,
            "details": f"Calculated shift: {delta_pct:.1f}%" if previous_val else "No prior history"
        })

        # Final Verdict Resolution
        if range_pass and delta_pass and not lipemia:
            return {
                "verdict": DecisionVerdict.AUTO_VALIDATED,
                "reason": "All physiological, preanalytical, and delta rules passed.",
                "trace": trace,
            }
        else:
            reasons = []
            if not range_pass:
                reasons.append(f"Value {current_val} out of reference range")
            if not delta_pass:
                reasons.append(f"Delta shift of {delta_pct:.1f}% exceeds limit ({cfg.delta_limit_pct}%)")
            if lipemia:
                reasons.append("Sample lipemia flagged for manual inspection")

            return {
                "verdict": DecisionVerdict.MANUAL_REVIEW,
                "reason": "; ".join(reasons),
                "trace": trace,
            }

    def simulate_cohort(self, analyte: str, n_samples: int = 1000, random_seed: int = 42) -> pd.DataFrame:
        """Runs a Monte Carlo synthetic cohort simulation."""
        np.random.seed(random_seed)
        cfg = self.registry[analyte]

        values = np.random.normal(cfg.pop_mean, cfg.pop_sd, n_samples).round(2)
        hemo_flags = np.random.rand(n_samples) < 0.03
        lip_flags = np.random.rand(n_samples) < 0.02
        clot_flags = np.random.rand(n_samples) < 0.005

        results = []
        for i in range(n_samples):
            prev_val = round(values[i] * np.random.uniform(0.92, 1.08), 2) if np.random.rand() > 0.3 else None
            res = self.evaluate_sample(
                analyte=analyte,
                current_val=values[i],
                previous_val=prev_val,
                hemolysis=bool(hemo_flags[i]),
                lipemia=bool(lip_flags[i]),
                clot_alert=bool(clot_flags[i]),
            )
            results.append({
                "sample_id": i + 1,
                "value": values[i],
                "verdict": res["verdict"].value,
                "reason": res["reason"]
            })

        return pd.DataFrame(results)
