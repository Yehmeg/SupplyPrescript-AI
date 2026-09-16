const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

const ROOT_API =
  import.meta.env.VITE_API_ROOT_URL ||
  API_BASE.replace(/\/api\/v1\/?$/, "");


async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const error = new Error(
      data?.detail ||
      `API request failed (${response.status})`
    );

    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}


// ============================================================
// SYSTEM
// ============================================================

export async function getReadyStatus() {
  const response = await fetch(
    `${ROOT_API}/ready`,
    {
      cache: "no-store",
    }
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(
      data?.detail ||
      "Backend is not ready"
    );
  }

  return data;
}


// ============================================================
// ORDERS / ML
// ============================================================

export function predictOrders(payload) {
  return apiRequest(
    "/orders/predict",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}


export function getOrder(orderId) {
  return apiRequest(
    `/orders/${orderId}`
  );
}


export function getPrediction(predictionId) {
  return apiRequest(
    `/predictions/${predictionId}`
  );
}


export function getOrderPredictions(orderId) {
  return apiRequest(
    `/orders/${orderId}/predictions`
  );
}


// ============================================================
// OPTIMIZATION
// ============================================================

export function optimize(payload) {
  return apiRequest(
    "/optimize",
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}


export function getOptimizationRun(runId) {
  return apiRequest(
    `/optimization-runs/${runId}`
  );
}


export function getRecommendation(
  recommendationId
) {
  return apiRequest(
    `/recommendations/${recommendationId}`
  );
}


export function getRunRecommendations(runId) {
  return apiRequest(
    `/optimization-runs/${runId}/recommendations`
  );
}


// ============================================================
// CLOSED LOOP
// ============================================================

export function createDecision(
  recommendationId,
  payload
) {
  return apiRequest(
    `/recommendations/${recommendationId}/decision`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}


export function executeDecision(decisionId) {
  return apiRequest(
    `/decisions/${decisionId}/execute`,
    {
      method: "POST",
    }
  );
}


export function recordOutcome(
  decisionId,
  payload
) {
  return apiRequest(
    `/decisions/${decisionId}/outcome`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    }
  );
}


export function getDecisionROI(decisionId) {
  return apiRequest(
    `/decisions/${decisionId}/roi`
  );
}