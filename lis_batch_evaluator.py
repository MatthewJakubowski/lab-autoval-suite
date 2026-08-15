"""
LIS Batch Anonymizer & Autovalidation Evaluator
Processes raw anonymized LIS CSV exports to measure real-world AVR & time savings.
"""

import sys
import pandas as pd
from engine import LabDecisionEngine, DecisionVerdict


def evaluate_lis_export(csv_path: str, seconds_per_manual_val: float = 20.0):
    engine = LabDecisionEngine()
    df = pd.read_csv(csv_path)

    # Required columns check
    required_cols = {"analyte", "value"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain at least: {required_cols}")

    verdicts = []
    reasons = []

    for _, row in df.iterrows():
        analyte = str(row["analyte"]).strip().upper()
        val = float(row["value"])
        prev_val = float(row["prev_value"]) if "prev_value" in row and pd.notna(row["prev_value"]) else None
        hemo = bool(row["flag_hemolysis"]) if "flag_hemolysis" in row and pd.notna(row["flag_hemolysis"]) else False
        lip = bool(row["flag_lipemia"]) if "flag_lipemia" in row and pd.notna(row["flag_lipemia"]) else False
        clot = bool(row["flag_clot"]) if "flag_clot" in row and pd.notna(row["flag_clot"]) else False

        try:
            res = engine.evaluate_sample(
                analyte=analyte,
                current_val=val,
                previous_val=prev_val,
                hemolysis=hemo,
                lipemia=lip,
                clot_alert=clot,
            )
            verdicts.append(res["verdict"].value)
            reasons.append(res["reason"])
        except ValueError:
            verdicts.append(DecisionVerdict.MANUAL_REVIEW.value)
            reasons.append("Unconfigured analyte code")

    df["system_verdict"] = verdicts
    df["system_reason"] = reasons

    total = len(df)
    avr_count = (df["system_verdict"] == DecisionVerdict.AUTO_VALIDATED.value).sum()
    manual_count = (df["system_verdict"] == DecisionVerdict.MANUAL_REVIEW.value).sum()
    reject_count = (df["system_verdict"] == DecisionVerdict.REJECT_PREANALYTIC.value).sum()

    avr_pct = (avr_count / total) * 100.0
    hours_saved = (avr_count * seconds_per_manual_val) / 3600.0

    print("=" * 60)
    print("  LIS BATCH EVALUATION REPORT (ISO 15189)")
    print("=" * 60)
    print(f"Total Processed Samples:     {total:,}")
    print(f"Auto-Validated (AVR):        {avr_count:,} ({avr_pct:.1f}%)")
    print(f"Manual Review Flagged:       {manual_count:,} ({(manual_count/total)*100:.1f}%)")
    print(f"Preanalytical Rejections:    {reject_count:,} ({(reject_count/total)*100:.1f}%)")
    print(f"Estimated Staff Time Saved:  ~{hours_saved:.1f} hours")
    print("=" * 60)

    output_csv = "lis_evaluated_results.csv"
    df.to_csv(output_csv, index=False)
    print(f"Full audit log written to: {output_csv}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        evaluate_lis_export(sys.argv[1])
    else:
        print("Usage: python lis_batch_evaluator.py <path_to_anonymized_lis_export.csv>")
