# SupplyPrescript

## Predictive Supply-Chain Risk & Prescriptive Intervention System

SupplyPrescript is a machine-learning-based supply-chain analytics
project designed to predict the risk of late delivery and support
downstream operational decisions.

The project has two main layers:

1.  **Predictive Layer** --- estimates the probability that an order
    will be delivered late.
2.  **Optimization / Prescriptive Layer** --- uses predicted risk
    together with intervention cost, late-delivery penalty, capacity
    constraints, and SLA requirements to decide whether an intervention
    is worthwhile.

------------------------------------------------------------------------

## Current Status

**ML Version:** V2\
**Status:** Baseline locked; optimization/prescriptive layer is the next
stage.

### Current V2 untouched-test performance

  Metric         Score
  ----------- --------
  Accuracy      56.90%
  Precision     56.84%
  Recall        98.98%
  F1 Score      72.22%
  ROC-AUC       73.74%

**Validation-selected classification threshold:** approximately `0.18`.

The low threshold strongly favors recall, which produces many
false-positive late-risk predictions. Therefore, the threshold-dependent
metrics should be interpreted together with the project's operational
objective.

------------------------------------------------------------------------

## Problem Statement

Late deliveries can cause customer dissatisfaction, SLA violations,
additional logistics costs, operational disruption, and lost revenue.

SupplyPrescript aims to move beyond simply predicting whether an order
is late. The system is designed to answer:

> **Which potentially risky orders are worth intervening on?**

------------------------------------------------------------------------

## System Architecture

``` text
Supply-Chain Data
       |
       v
Data Cleaning & Preparation
       |
       v
Order-Level Grouping
       |
       v
Group-Aware Train / Validation / Test Split
       |
       v
Feature Engineering
       |
       +----------------+----------------+
       |                |                |
       v                v                v
    XGBoost          LightGBM         CatBoost
       |                |                |
       +----------------+----------------+
                        |
                        v
              Ensemble Risk Probability
                        |
                        v
             Validation Thresholding
                        |
                        v
                 Late-Risk Score
                        |
                        v
              Optimization Layer
                        |
       +----------------+----------------+
       |                |                |
       v                v                v
 Risk Probability  Intervention Cost  Late Penalty
       |                |                |
       +----------------+----------------+
                        |
                Capacity Constraints
                        |
                        v
                  SLA Requirements
                        |
                        v
              Recommended Intervention
```

------------------------------------------------------------------------

## Dataset

The project uses supply-chain order/line-item information including
variables related to:

-   scheduled shipping duration,
-   customer and order locations,
-   market and region,
-   customer segment,
-   product/category information,
-   sales and profit,
-   order dates,
-   geographic information,
-   shipment-related attributes.

The target variable is:

``` text
Late_delivery_risk
```

where:

``` text
0 = Not Late
1 = Late
```

------------------------------------------------------------------------

## Leakage-Safe Evaluation

A major focus of V2 is preventing overly optimistic performance.

Multiple rows can belong to the same underlying order. Therefore, the
pipeline uses order grouping so that records from the same order group
do not cross the training, validation, and testing partitions.

The evaluation workflow is:

``` text
TRAIN
  -> model fitting and tuning

VALIDATION
  -> model/feature decisions
  -> threshold selection

TEST
  -> final evaluation only
```

The test set is kept untouched during model and threshold selection.

------------------------------------------------------------------------

## Feature Decisions

### Shipping Mode vs Scheduled Shipping Days

`Shipping Mode` and `Days for shipment (scheduled)` provide highly
related information.

Validation comparison favored:

``` text
Days for shipment (scheduled)
```

Therefore, the current final representation keeps scheduled shipping
days and removes `Shipping Mode`.

### Order Status

`Order Status` was evaluated separately. The current V2 configuration
removes it because its availability at the exact prediction time has not
been established.

This avoids relying on information that may not be available when the
prediction is supposed to be made.

------------------------------------------------------------------------

## Predictive Models

The predictive layer uses:

### XGBoost

Gradient-boosted decision trees used as the primary model and tuned with
grouped cross-validation.

### LightGBM

A second gradient-boosting implementation used as an ensemble component.

### CatBoost

A gradient-boosting model particularly suited to datasets containing
categorical variables.

### Ensemble

The current ensemble combines model probabilities:

``` text
Ensemble Probability =
(XGBoost Probability
 + LightGBM Probability
 + CatBoost Probability) / 3
```

------------------------------------------------------------------------

## Threshold

The current validation-selected threshold is approximately:

``` text
0.18
```

This threshold prioritizes identifying late deliveries.

A lower threshold generally increases recall but can also increase false
positives.

Threshold changes can affect:

-   Accuracy
-   Precision
-   Recall
-   F1

but do not normally change ROC-AUC.

Therefore, threshold tuning should not be confused with improving the
underlying predictive discrimination of the model.

------------------------------------------------------------------------

## Why the Optimization Layer Matters

The ML model answers:

> **How likely is this order to be late?**

The optimization layer answers:

> **Is intervention worthwhile?**

For example, an order with moderate late-risk may not justify an
expensive intervention. A lower-risk order may still justify
intervention if the SLA penalty is large and the intervention is cheap.

The optimization layer is therefore built around:

``` text
Risk Probability
+
Intervention Cost
+
Late-Delivery Penalty
+
Available Capacity
+
SLA Constraints
```

The desired output is an operational recommendation such as:

``` text
INTERVENE
```

or:

``` text
DO NOT INTERVENE
```

rather than treating every probability above `0.18` identically.

------------------------------------------------------------------------

## Current Result Interpretation

The V2 model has:

``` text
ROC-AUC ≈ 0.74
```

which indicates predictive signal above random ranking.

The current classification behavior is strongly recall-oriented:

``` text
Recall ≈ 99%
Precision ≈ 57%
```

Therefore, V2 is treated as a **validated baseline**, not as a claim
that the predictive model is already optimal.

The next project stage is the prescriptive optimization layer.

------------------------------------------------------------------------

## Evaluation Metrics

### Accuracy

Percentage of correctly classified orders.

### Precision

Among orders predicted as late, the percentage that are actually late.

### Recall

Among orders that are actually late, the percentage detected by the
model.

### F1 Score

Harmonic mean of precision and recall.

### ROC-AUC

Measures the model's ability to rank late orders above non-late orders
across thresholds.

------------------------------------------------------------------------

## Project Roadmap

### Phase 1 --- Predictive Baseline

-   [x] Data cleaning
-   [x] Feature preparation
-   [x] Group-aware splitting
-   [x] XGBoost
-   [x] LightGBM
-   [x] CatBoost
-   [x] Ensemble
-   [x] Validation threshold selection
-   [x] Untouched test evaluation
-   [x] Leakage checks

### Phase 2 --- Prescriptive Optimization

-   [ ] Define intervention actions
-   [ ] Define intervention costs
-   [ ] Define late-delivery penalties
-   [ ] Define available intervention capacity
-   [ ] Define SLA constraints
-   [ ] Build the optimization objective
-   [ ] Generate recommended interventions
-   [ ] Evaluate operational benefit

### Phase 3 --- Optional Model Improvement

If project time permits:

-   [ ] Improve logistics-related features
-   [ ] Tune LightGBM
-   [ ] Tune CatBoost
-   [ ] Optimize ensemble weights
-   [ ] Re-evaluate using validation data
-   [ ] Perform one final untouched-test evaluation

------------------------------------------------------------------------

## Repository Structure

``` text
SupplyPrescript/
│
├── README.md
├── notebooks/
│   └── SupplyPrescript_ML_V2.ipynb
│
├── data/
│   └── README.md
│
├── models/
│   └── README.md
│
├── src/
│   ├── preprocessing.py
│   ├── modeling.py
│   ├── evaluation.py
│   └── optimization.py
│
├── results/
│   ├── metrics/
│   └── figures/
│
└── requirements.txt
```

------------------------------------------------------------------------

## Project Principle

SupplyPrescript prioritizes **honest, leakage-safe evaluation over
artificially maximizing metrics**.

The objective is to build a model that generalizes to genuinely unseen
orders and then use its risk estimates to make economically and
operationally meaningful intervention decisions.

------------------------------------------------------------------------

## Disclaimer

V2 represents the current experimental baseline under the project's
group-aware evaluation setup. The system should not be treated as a
production decision engine until prediction-time feature availability,
intervention costs, capacity constraints, and SLA assumptions are
formally defined and validated.
