# LabAutoVal Suite 🔬⚡️
> Deterministic Explainable AI (XAI) & Autovalidation Architecture for Clinical Diagnostics (ISO 15189 Aligned).

[![Hugging Face Space](https://img.shields.io/badge/Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/matthewjakubowski/lab-autoval-suite)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview
In high-throughput diagnostic laboratory networks processing >100,000 orders/month, medical diagnosticians face severe decision fatigue routinely clicking through normal, non-pathological results. 

**LabAutoVal Suite** provides a transparent, deterministic rule-cascade engine designed to safely autovalidate normal diagnostic samples while flagging critical anomalies and preanalytical interferences (HIL) for human review.

### 🌐 Live Interactive Demo & Executive Brief
* 🚀 **Interactive Simulator:** [Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/matthewjakubowski/lab-autoval-suite)
* 📄 **Executive Summary (PL/EN):** [Download LabAutoVal_Executive_Summary.pdf](./LabAutoVal_Executive_Summary.pdf)

---

## ⚖️ Legal & Research Disclaimer (Proof of Concept)
> **Educational & Simulation Notice:** This repository is an engineering Proof of Concept (PoC) developed strictly for educational, research, and workflow modeling purposes. It does not constitute a certified in vitro medical device (IVDR) software.

---

## 🔬 Rule Cascade Matrix (ISO 15189)

```text
[ Incoming LIS Result ]
          │
          ▼
┌─────────────────────────────────┐
│ 1. Preanalytics & Clot Alert    │ ── (Failed: HIL/Clot) ──► 🔴 REJECT_PREANALYTIC
└─────────────────────────────────┘
          │ (Passed)
          ▼
┌─────────────────────────────────┐
│ 2. Reference Range Check        │ ── (Out of Range)     ──► 🟡 MANUAL_REVIEW
└─────────────────────────────────┘
          │ (Passed)
          ▼
┌─────────────────────────────────┐
│ 3. Dynamic Delta Check          │ ── (Delta > Limit)    ──► 🟡 MANUAL_REVIEW
└─────────────────────────────────┘
          │ (Passed)
          ▼
  🟢 AUTO_VALIDATED (Instant LIS Clearance)

```
---

## 🛠️ Project Structure
```text
├── engine.py                  # Core deterministic decision engine & Monte Carlo simulator
├── test_engine.py             # Pytest test suite for rule validation
├── lis_batch_evaluator.py     # LIS CSV batch processing & ROI evaluator
├── LabAutoVal_Executive_Summary.pdf # One-page bi-lingual executive brief
└── README.md                  # Project documentation

```

## 🚀 Getting Started
# ​1. Installation
```bash
git clone [https://github.com/matthewjakubowski/lab-autoval-suite.git](https://github.com/matthewjakubowski/lab-autoval-suite.git)
cd lab-autoval-suite
pip install pandas numpy pytest
```

# 2. Run Test Suite
```bash
pytest test_engine.py -v
```

# 3. Evaluate LIS Export (Batch Mode)
```bash
python lis_batch_evaluator.py sample_lis_export.csv
```
## 👨‍💻 Author & Connect

| **Mateusz (Matthew) Jakubowski** |
| :--- |
| *Senior Laboratory Technologist & Data Science Explorer* |
| 🏷️ **Campaign:** `#FromPipetteToPython` |
| 🌐 **Portfolio Hub:** [mateusz-jakubowski.ai.studio](https://mateusz-jakubowski.ai.studio/) |
| 🚀 **Project Showroom:** [from-pipette-to-python.ai.studio](https://from-pipette-to-python.ai.studio/) |
| 💼 **LinkedIn:** [mateuszjakubowski](https://www.linkedin.com/in/mateuszjakubowski) |
| 🐙 **GitHub:** [@MatthewJakubowski](https://github.com/MatthewJakubowski) |
| 🤗 **Hugging Face:** [@matthewjakubowski](https://huggingface.co/matthewjakubowski) |
| 📊 **Kaggle:** [@matthewjakubowski](https://www.kaggle.com/matthewjakubowski) |
| 🐦 **X (Twitter):** [@M_S_Jakubowski](https://x.com/M_S_Jakubowski) |
| 🍷 **Vivino:** [mateusz.jakubowski](http://www.vivino.com/users/mateusz.jakubowski/) |

---


---
