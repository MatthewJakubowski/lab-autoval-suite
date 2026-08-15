import pytest
from engine import LabDecisionEngine, DecisionVerdict


@pytest.fixture
def engine():
    return LabDecisionEngine()


def test_glucose_normal_autovalidation(engine):
    res = engine.evaluate_sample("GLU", current_val=85.0, previous_val=82.0)
    assert res["verdict"] == DecisionVerdict.AUTO_VALIDATED
    assert len(res["trace"]) == 3


def test_hemolysis_rejection(engine):
    res = engine.evaluate_sample("K", current_val=4.2, hemolysis=True)
    assert res["verdict"] == DecisionVerdict.REJECT_PREANALYTIC


def test_delta_check_trigger(engine):
    # Potassium jumping from 4.0 to 4.9 is a 22.5% increase (> 15% limit)
    res = engine.evaluate_sample("K", current_val=4.9, previous_val=4.0)
    assert res["verdict"] == DecisionVerdict.MANUAL_REVIEW
    assert "Delta shift" in res["reason"]


def test_cohort_simulation_size(engine):
    df = engine.simulate_cohort("GLU", n_samples=500)
    assert len(df) == 500
    assert "AUTO_VALIDATED" in df["verdict"].unique()
