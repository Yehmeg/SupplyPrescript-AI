# SupplyPrescript — Section 1: Data Foundation

## 1. Overview

This section establishes the data foundation for the SupplyPrescript project.

The work covers:

- Data ingestion
- Data cleaning
- Data quality analysis
- Feature engineering
- Target preparation
- Data leakage checks
- Final dataset validation
- Reusable preprocessing modules

The processed dataset will be used by the later machine-learning module.

---

## 2. Dataset

### Dataset Used

The project uses a historical supply-chain shipment dataset containing order, shipment, customer, product, and delivery-related information.

### Original Dataset Size

- Rows: **180,519**
- Columns: **53**

### Target Variable

```text
Late_delivery_risk


