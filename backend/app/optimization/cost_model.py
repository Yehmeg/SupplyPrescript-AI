def calculate_baseline_expected_loss(
    late_probability: float,
    late_penalty: float
) -> float:
    return late_probability * late_penalty


def calculate_risk_after_action(
    late_probability: float,
    risk_reduction: float
) -> float:
    return late_probability * (1 - risk_reduction)


def calculate_expected_cost_after_action(
    action_cost: float,
    risk_after_action: float,
    late_penalty: float
) -> float:
    expected_late_loss = risk_after_action * late_penalty

    return action_cost + expected_late_loss


def calculate_expected_saving(
    baseline_expected_loss: float,
    expected_cost_after_action: float
) -> float:
    return baseline_expected_loss - expected_cost_after_action