# SupplyPrescript --- Machine Learning

## What this branch contains

This branch contains the **Machine Learning development and
experimentation for SupplyPrescript**.

The purpose of this work is not only to train a model, but to document:

-   which models were tried,
-   why each model/approach was tested,
-   what results were obtained,
-   what was rejected and why,
-   how overfitting and leakage were investigated,
-   why the final V2 pipeline was selected,
-   and how the ML output will be used by the next optimization layer.

The final ML output is a **late-delivery risk probability** for an
order.

------------------------------------------------------------------------

# 1. Problem Definition

The target variable is:

``` text
Late_delivery_risk
```

with:

``` text
0 → Not Late
1 → Late
```

The objective is to estimate the probability that an order will be
delivered late.

The ML model is only the **predictive layer** of SupplyPrescript.

It answers:

> **How likely is this order to be late?**

The later optimization layer will answer:

> **Is intervention worth doing for this order?**

------------------------------------------------------------------------

# 2. Dataset and Features

The project uses the DataCo Supply Chain dataset.

The data contains information related to:

-   customer information,
-   order information,
-   product/category information,
-   market and geographic information,
-   sales and profit,
-   order dates,
-   scheduled shipment duration,
-   customer/order locations,
-   categorical and numerical variables.

Important prediction-time features include:

``` text
Days for shipment (scheduled)
Customer City
Customer State
Customer Country
Order City
Order State
Order Country
Order Region
Market
Customer Segment
Product information
Sales / profit-related features
Order date features
Geographic features
```

------------------------------------------------------------------------

# 3. First Approach --- Initial XGBoost Experiments

We started with **XGBoost** because the dataset is primarily tabular and
contains a mixture of numerical and categorical information after
preprocessing.

The first goal was to establish a strong baseline and then investigate
overfitting.

We experimented with:

-   tree depth,
-   number of estimators,
-   learning rate,
-   minimum child weight,
-   subsampling,
-   column subsampling,
-   gamma,
-   L1 regularization,
-   L2 regularization.

------------------------------------------------------------------------

# 4. Overfitting Investigation

One of the main team requirements was:

> **Reduce the training--testing performance gap without sacrificing too
> much predictive performance.**

Therefore, we did not judge models only by their test score.

We also compared:

``` text
Training F1 vs Testing F1
Training ROC-AUC vs Testing ROC-AUC
```

The gaps were explicitly calculated.

------------------------------------------------------------------------

## XGBoost V2

One tuned configuration used:

``` python
n_estimators = 400
max_depth = 6
learning_rate = 0.06
min_child_weight = 5
subsample = 0.8
colsample_bytree = 0.8
gamma = 0.1
reg_alpha = 1
reg_lambda = 2
```

Results:

``` text
Training Accuracy : 0.8423
Testing Accuracy  : 0.7947

Training F1       : 0.8479
Testing F1        : 0.7994

Training ROC-AUC  : 0.9302
Testing ROC-AUC   : 0.8827

F1 Gap             : 0.0485
ROC-AUC Gap        : 0.0475
```

### Decision

This was a useful improvement in controlling overfitting.

The training and testing scores were reasonably close, while the testing
performance remained useful.

This configuration was therefore kept as an important XGBoost reference
point.

------------------------------------------------------------------------

# 5. Mild Regularization Experiment

We also tested a milder regularization configuration to see whether
performance could be increased while maintaining a reasonable
generalization gap.

Results:

``` text
Training Accuracy : 0.9468
Testing Accuracy  : 0.8667

Training F1       : 0.9507
Testing F1        : 0.8749

Training ROC-AUC  : 0.9896
Testing ROC-AUC   : 0.9419

F1 Gap             : 0.0759
ROC-AUC Gap        : 0.0477
```

### Decision

Although the raw test performance looked attractive, the F1
training--testing gap increased to approximately:

``` text
0.0759
```

compared with:

``` text
0.0485
```

for the previous XGBoost V2 configuration.

### Why it was not selected

The goal was not simply to maximize the test score.

We wanted a model with a better balance between:

``` text
Performance
+
Generalization
```

Therefore, this configuration was not preferred as the final direction.

------------------------------------------------------------------------

# 6. XGBoost + LightGBM Ensemble

Next, we tested whether combining different tree-based models could
improve generalization.

The first ensemble combined:

``` text
XGBoost
+
LightGBM
```

using averaged probabilities.

Results:

``` text
Training Accuracy : 0.9476
Testing Accuracy  : 0.8740

Training F1       : 0.9527
Testing F1        : 0.8853

Training ROC-AUC  : 0.9881
Testing ROC-AUC   : 0.9428

F1 Gap             : 0.0674
ROC-AUC Gap        : 0.0452
```

Compared with the tuned XGBoost:

  Metric        Tuned XGBoost   XGBoost + LightGBM
  ----------- --------------- --------------------
  Accuracy             0.8703           **0.8740**
  Precision        **0.9054**               0.8837
  Recall               0.8524           **0.8869**
  F1                   0.8781           **0.8853**
  ROC-AUC          **0.9442**               0.9428

### Decision

The ensemble improved:

-   Accuracy slightly
-   Recall
-   F1

but did not improve ROC-AUC over the tuned XGBoost.

It was nevertheless useful because it demonstrated that combining models
could improve the balance between precision and recall.

------------------------------------------------------------------------

# 7. Three-Model Ensemble

We then added CatBoost:

``` text
XGBoost
+
LightGBM
+
CatBoost
```

The three model probabilities were averaged.

Results from the earlier evaluation were:

``` text
Training Accuracy : 0.9798
Testing Accuracy  : 0.9237

Training F1       : 0.9816
Testing F1        : 0.9304

Training ROC-AUC  : 0.9978
Testing ROC-AUC   : 0.9770

F1 Gap             : 0.0513
ROC-AUC Gap        : 0.0208
```

At the selected threshold of `0.45`:

``` text
Accuracy  : 0.9237
Precision : 0.9314
Recall    : 0.9293
F1        : 0.9304
ROC-AUC   : 0.9770
```

This looked substantially better than the previous experiments.

However, this result raised an important question:

> **Is the very high performance genuine, or is the random row-level
> split allowing related records from the same order to appear in both
> training and testing?**

This question led to the next major change in the project.

------------------------------------------------------------------------

# 8. Leakage Investigation

Because the dataset can contain multiple records belonging to the same
underlying order, a random row split can make the prediction task
artificially easy.

Therefore, we performed a more rigorous evaluation.

The V2 pipeline uses:

``` text
TRAIN
   ↓
Model training / tuning

VALIDATION
   ↓
Model and threshold selection

TEST
   ↓
Final evaluation only
```

and uses **order-level grouping** to prevent related order records from
crossing the dataset partitions.

The pipeline checks:

-   target leakage,
-   train/test overlap,
-   duplicate rows,
-   cross-split group overlap,
-   suspicious feature names,
-   feature consistency,
-   prediction-time feature availability.

The final leakage audit showed:

``` text
Target in features       : False
Train/Test overlap       : 0
Duplicate rows           : 0
Group overlap            : 0
Feature consistency      : PASS
```

------------------------------------------------------------------------

# 9. Why We Did Not Simply Keep the 0.97 AUC Result

The earlier three-model result was much higher:

``` text
ROC-AUC ≈ 0.977
```

However, it came from the earlier evaluation setup.

The stricter group-aware evaluation is more representative of the real
objective:

> **Can the model generalize to genuinely unseen orders?**

Therefore, we did not choose the highest number simply because it was
higher.

We chose a more defensible evaluation protocol.

This is an important project decision.

------------------------------------------------------------------------

# 10. V2 Group-Aware Model Pipeline

The current V2 pipeline uses:

``` text
XGBoost
+
LightGBM
+
CatBoost
```

with group-aware train/validation/test separation.

The test set remains untouched until the model and threshold are locked.

This gives us a more conservative but more defensible estimate of
real-world predictive performance.

------------------------------------------------------------------------

# 11. Feature Decisions

## Shipping Mode vs Scheduled Shipping Days

`Shipping Mode` and:

``` text
Days for shipment (scheduled)
```

contain highly related information.

We tested them and retained:

``` text
Days for shipment (scheduled)
```

while removing:

``` text
Shipping Mode
```

This avoids unnecessary duplication without sacrificing the useful
shipment-duration signal.

------------------------------------------------------------------------

## Order Status

`Order Status` was also investigated.

It was removed from the final V2 feature set because its availability at
the intended prediction time was not established.

This is important because a feature that becomes available only after
the prediction decision should not be used to claim a real pre-shipment
prediction.

The comparison also showed that adding Order Status did not provide a
large enough improvement to justify the prediction-time uncertainty.

------------------------------------------------------------------------

# 12. Current V2 Threshold

The final V2 threshold selected using validation data is:

``` text
0.18
```

This is deliberately recall-oriented.

The model therefore behaves approximately as:

``` text
Predicted probability >= 0.18
            ↓
          LATE
```

This produces:

``` text
Very high recall
+
More false positives
```

The threshold is not considered the final business intervention rule.

------------------------------------------------------------------------

# 13. Final V2 Test Results

The final V2 model was evaluated once on the untouched test set.

``` text
==================================================
FINAL V2 RESULTS
==================================================

Accuracy  : 56.90%
Precision : 56.84%
Recall    : 98.98%
F1 Score  : 72.22%
ROC-AUC   : 73.74%

Threshold : 0.18
```

### Interpretation

The most important measure of underlying ranking capability here is:

``` text
ROC-AUC ≈ 0.74
```

This indicates useful predictive signal above random ranking.

The classification metrics are strongly affected by the low threshold:

``` text
Recall    ≈ 99%
Precision ≈ 57%
```

Therefore, the current V2 should be described as a:

> **Leakage-safe validated ML baseline**

rather than an already-optimal predictive model.

------------------------------------------------------------------------

# 14. Why We Are Keeping V2

We are keeping V2 because the purpose of this stage is to establish a
reliable predictive foundation.

The validation and untouched-test ROC-AUC are close:

``` text
Validation ROC-AUC ≈ 0.740
Test ROC-AUC       ≈ 0.737
```

This indicates that the model is behaving consistently between
validation and unseen test data under the stricter evaluation setup.

The goal at this stage is therefore:

``` text
Reliable probability
        ↓
Optimization layer
        ↓
Business decision
```

rather than continuing to tune the ML model indefinitely.

------------------------------------------------------------------------

# 15. Why We Are Not Treating 0.18 as an Intervention Rule

The model probability and the business decision are two different
things.

For example:

``` text
Order A
Risk = 0.20
```

does not automatically mean:

``` text
INTERVENE
```

Instead, the next layer should consider:

``` text
Risk Probability
+
Intervention Cost
+
Late-Delivery Penalty
+
Available Capacity
+
SLA Requirements
```

and determine whether intervention is worthwhile.

Therefore:

``` text
ML Layer
→ predicts risk

Optimization Layer
→ decides what to do
```

This prevents every order above the classification threshold from being
treated identically.

------------------------------------------------------------------------

# 16. Current ML Decision

## LOCKED: V2 Predictive Baseline

The current V2 pipeline is locked for the next project stage.

Completed:

-   [x] Data cleaning
-   [x] Feature preparation
-   [x] XGBoost experiments
-   [x] Overfitting analysis
-   [x] LightGBM
-   [x] CatBoost
-   [x] Ensemble experiments
-   [x] Leakage investigation
-   [x] Group-aware splitting
-   [x] Validation threshold selection
-   [x] Untouched test evaluation
-   [x] Final leakage audit

------------------------------------------------------------------------

# 17. What We Learned

### Model selection

A higher test score is not automatically a better model.

We need to consider:

``` text
Predictive performance
+
Generalization
+
Leakage risk
+
Prediction-time availability
```

### Overfitting

Changing depth and regularization helped us understand the trade-off
between:

``` text
Training performance
vs
Testing performance
```

### Ensemble learning

Combining XGBoost, LightGBM, and CatBoost can improve predictive
performance, but ensemble results must still be evaluated under a
leakage-safe split.

### Threshold

A threshold controls the classification trade-off.

It does not improve the underlying ROC-AUC.

### Leakage

A stricter group-aware split can produce lower but more realistic
performance than a random row split.

This is preferable to reporting an inflated score.

------------------------------------------------------------------------

# 18. Next Step: Optimization Layer

The next stage is not to keep changing the threshold.

The ML model now supplies:

``` text
Late-Risk Probability
```

The optimization layer will use this probability with:

``` text
Intervention Cost
Late-Delivery Penalty
Capacity Constraints
SLA Constraints
```

to generate an intervention decision/recommendation.

The intended flow is:

``` text
New Order
    ↓
ML Model
    ↓
Late-Risk Probability
    ↓
Optimization
    ↓
Feasible Actions
    ↓
Cost / Benefit Comparison
    ↓
Recommended Action
```

------------------------------------------------------------------------

# 19. Future ML Improvements

If time permits, future versions can investigate:

-   stronger logistics feature engineering,
-   tuning LightGBM and CatBoost under grouped validation,
-   validation-based ensemble weight optimization,
-   improved probability calibration,
-   additional legitimate prediction-time features,
-   monitoring performance after new outcome data becomes available.

Any future model must follow the same leakage-safe evaluation
principles.

------------------------------------------------------------------------

# 20. Final ML Summary

The ML development progressed through:

``` text
Initial XGBoost
      ↓
Overfitting / regularization experiments
      ↓
XGBoost tuning
      ↓
XGBoost + LightGBM
      ↓
XGBoost + LightGBM + CatBoost
      ↓
Leakage investigation
      ↓
Group-aware V2
      ↓
Validation threshold
      ↓
Untouched test
      ↓
V2 locked
```

### Current final baseline

``` text
Models:
XGBoost + LightGBM + CatBoost

Evaluation:
Group-aware train / validation / test

Threshold:
0.18

Test ROC-AUC:
0.7374

Test F1:
0.7222

Test Recall:
0.9898
```

The V2 ML model is now ready to provide the risk probabilities required
by the **SupplyPrescript optimization layer**.
