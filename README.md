# SupplyPrescript-AI
AI-powered Supply Chain Decision Support System


## Closed-Loop Prescriptive Analytics for Supply Chain Operations

SupplyPrescript is a decision-support platform designed for supply chain and logistics operations.

Traditional predictive analytics can tell an operator that a shipment is likely to be delayed, but they often stop at prediction. SupplyPrescript aims to go one step further:

> **Predict → Explain → Prescribe → Decide → Measure → Learn**

The system predicts shipment delay risk, identifies contributing factors, generates feasible corrective actions using constrained optimization, records the human decision, evaluates the actual outcome, and uses the accumulated outcomes to improve future decisions.

---

# 1. Problem Statement

Supply chain dashboards commonly provide predictive information such as:

> "Shipment X has a high probability of being delayed."

However, the operator still has to decide what action to take.

For example, if a shipment containing critical microchips is expected to be delayed, the operator may need to decide between:

- Expediting through air freight
- Switching to a secondary supplier
- Changing the shipment plan
- Accepting the delay

Traditional dashboards generally do not systematically record which action was selected or whether that action actually created business value.

SupplyPrescript addresses this gap by connecting prediction, optimization, human decision-making, outcome tracking, and model improvement into one closed loop.

---

# 2. Project Objectives

SupplyPrescript aims to:

1. Predict whether a shipment is likely to be delayed.
2. Estimate the expected delay.
3. Identify important factors contributing to the prediction.
4. Generate feasible corrective actions.
5. Rank the top three actions using business constraints.
6. Allow an operator to accept or reject a recommendation.
7. Store the selected decision.
8. Record the actual shipment outcome.
9. Calculate the business value / ROI of the decision.
10. Use historical outcomes to improve future predictions and recommendations.

---

# 3. Core Workflow

```text
Historical Shipment Data
          |
          v
Data Ingestion
          |
          v
Data Cleaning
          |
          v
Feature Engineering
          |
          v
Delay Prediction
          |
          v
Delay Explanation
          |
          v
Optimization Engine
          |
          v
Top 3 Recommendations
          |
          v
Human Decision
     Accept / Reject
          |
          v
Decision Stored
          |
          v
Actual Shipment Outcome
          |
          v
ROI / Business Value
          |
          v
Model & Recommendation Improvement
ijhuiykj
