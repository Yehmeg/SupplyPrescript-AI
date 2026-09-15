import React, {
  useEffect,
  useMemo,
  useState,
} from "react";

import { createRoot } from "react-dom/client";

import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/components.css";
import "./styles/layout.css";
import "./styles/legacy.css";
import "./styles/integration.css";

import { useToast } from "./hooks/useToast";

import {
  ToastContainer,
} from "./components/ui/Toast";

import {
  ErrorBoundary,
} from "./components/ui/ErrorBoundary";

import {
  createDecision,
  executeDecision,
  getDecisionROI,
  getOrderPredictions,
  getReadyStatus,
  getRecommendation,
  getRunRecommendations,
  optimize,
  recordOutcome,
} from "./services/api";


const DEFAULT_ORDER_ID = Number(
  import.meta.env.VITE_DEMO_ORDER_ID || 1
);

const DEFAULT_RUN_ID = Number(
  import.meta.env.VITE_DEMO_RUN_ID || 1
);

const DEFAULT_DECISION_ID = Number(
  import.meta.env.VITE_DEMO_DECISION_ID || 1
);

const WORKFLOW_KEY =
  "supplyprescript.workflow";

const RUN_KEY =
  "supplyprescript.runId";

const CONSTRAINT_KEY =
  "supplyprescript.constraints";


function readStorage(key, fallback) {
  try {
    const value =
      localStorage.getItem(key);

    return value
      ? JSON.parse(value)
      : fallback;
  } catch {
    return fallback;
  }
}


function money(value) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  return Number(value).toLocaleString(
    "en-US",
    {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }
  );
}


function percent(value, digits = 2) {
  if (
    value === null ||
    value === undefined
  ) {
    return "—";
  }

  return `${Number(value).toFixed(digits)}%`;
}


function prettyAction(value = "") {
  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      c => c.toUpperCase()
    );
}


function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(value)
    .toLocaleString();
}


function mapRecommendation(rec) {
  const before =
    Number(rec.late_probability);

  const after =
    Number(rec.risk_after);

  const reduction =
    before > 0
      ? Math.round(
          ((before - after) / before) *
          100
        )
      : 0;

  return {
    id: rec.action_id,

    recommendationId:
      rec.recommendation_id,

    runId:
      rec.run_id,

    title:
      prettyAction(
        rec.selected_action
      ),

    selectedAction:
      rec.selected_action,

    tag:
      "Optimizer Selected",

    description:
      `Late risk reduced from ${
        (before * 100).toFixed(2)
      }% to ${
        (after * 100).toFixed(2)
      }%.`,

    score:
      Math.max(
        0,
        Math.min(
          100,
          reduction
        )
      ),

    cost:
      Number(rec.action_cost),

    days:
      rec.predicted_time_days ===
      null
        ? null
        : Number(
            rec.predicted_time_days
          ),

    riskAfter:
      after,

    expectedSaving:
      Number(rec.expected_saving),

    optimizedCost:
      Number(
        rec.optimized_expected_cost
      ),

    createdAt:
      rec.created_at,

    pros: [
      `Expected saving ${money(
        rec.expected_saving
      )}`,

      `Late risk reduced to ${
        (after * 100).toFixed(2)
      }%`,
    ],

    cons: [
      `Intervention cost ${money(
        rec.action_cost
      )}`,
    ],
  };
}


// ============================================================
// APP
// ============================================================

function App() {
  const [page, setPage] =
    useState("dashboard");

  const [
    backend,
    setBackend,
  ] = useState({
    online: false,
    checking: true,
    modelsLoaded: false,
    threshold: null,
  });

  const [
    dashboard,
    setDashboard,
  ] = useState({
    loading: true,
    error: null,
    order: null,
    prediction: null,
  });

  const [
    currentRunId,
    setCurrentRunId,
  ] = useState(() => {
    const saved =
      Number(
        localStorage.getItem(
          RUN_KEY
        )
      );

    return saved > 0
      ? saved
      : DEFAULT_RUN_ID;
  });

  const [
    optimization,
    setOptimization,
  ] = useState({
    loading: true,
    error: null,
    run: null,
    recommendations: [],
  });

  const [
    workflows,
    setWorkflows,
  ] = useState(() =>
    readStorage(
      WORKFLOW_KEY,
      {}
    )
  );

  const [
    selectedId,
    setSelectedId,
  ] = useState(null);

  const [
    outcomeTarget,
    setOutcomeTarget,
  ] = useState(null);

  const [
    refreshKey,
    setRefreshKey,
  ] = useState(0);

  const [
    optimizerBusy,
    setOptimizerBusy,
  ] = useState(false);

  const [
    constraints,
    setConstraints,
  ] = useState(() =>
    readStorage(
      CONSTRAINT_KEY,
      {
        totalBudget: 20000,
        latePenalty: 10000,
        baselineTimeDays: 5,

        expediteCapacity: 1,
        priorityCapacity: 1,
        routeCapacity: 1,
        hubCapacity: 1,

        expediteAvailable: true,
        priorityAvailable: true,
        routeAvailable: true,
        hubAvailable: true,
      }
    )
  );

  const {
    toasts,
    showToast,
    dismissToast,
  } = useToast();


  useEffect(() => {
    localStorage.setItem(
      WORKFLOW_KEY,
      JSON.stringify(workflows)
    );
  }, [workflows]);


  useEffect(() => {
    localStorage.setItem(
      RUN_KEY,
      String(currentRunId)
    );
  }, [currentRunId]);


  useEffect(() => {
    localStorage.setItem(
      CONSTRAINT_KEY,
      JSON.stringify(constraints)
    );
  }, [constraints]);


  // ==========================================================
  // BACKEND STATUS
  // ==========================================================

  useEffect(() => {
    let active = true;

    async function check() {
      try {
        const data =
          await getReadyStatus();

        if (!active) return;

        setBackend({
          online: true,
          checking: false,
          modelsLoaded:
            Boolean(
              data.models_loaded
            ),
          threshold:
            data.threshold ?? null,
        });
      } catch {
        if (!active) return;

        setBackend({
          online: false,
          checking: false,
          modelsLoaded: false,
          threshold: null,
        });
      }
    }

    check();

    const interval =
      setInterval(
        check,
        15000
      );

    return () => {
      active = false;

      clearInterval(interval);
    };
  }, []);


  // ==========================================================
  // ORDER + PREDICTION
  // ==========================================================

  useEffect(() => {
    if (!backend.online) {
      if (!backend.checking) {
        setDashboard({
          loading: false,
          error:
            "Backend unavailable",
          order: null,
          prediction: null,
        });
      }

      return;
    }

    let active = true;

    async function load() {
      try {
        const data =
          await getOrderPredictions(
            DEFAULT_ORDER_ID
          );

        if (!active) return;

        setDashboard({
          loading: false,
          error: null,
          order:
            data.order ?? null,
          prediction:
            data.predictions?.[0] ??
            null,
        });
      } catch (error) {
        if (!active) return;

        setDashboard({
          loading: false,
          error: error.message,
          order: null,
          prediction: null,
        });
      }
    }

    load();

    return () => {
      active = false;
    };
  }, [
    backend.online,
    backend.checking,
    refreshKey,
  ]);


  // ==========================================================
  // OPTIMIZATION RUN
  // ==========================================================

  useEffect(() => {
    if (
      !backend.online ||
      !currentRunId
    ) {
      return;
    }

    let active = true;

    async function load() {
      try {
        const data =
          await getRunRecommendations(
            currentRunId
          );

        if (!active) return;

        setOptimization({
          loading: false,
          error: null,
          run:
            data.run ?? null,
          recommendations:
            data.recommendations ??
            [],
        });
      } catch (error) {
        if (!active) return;

        setOptimization({
          loading: false,
          error: error.message,
          run: null,
          recommendations: [],
        });
      }
    }

    load();

    return () => {
      active = false;
    };
  }, [
    backend.online,
    currentRunId,
    refreshKey,
  ]);


  // ==========================================================
  // EXISTING COMPLETED DEMO ROI
  // ==========================================================

  useEffect(() => {
    if (
      !backend.online ||
      !DEFAULT_DECISION_ID
    ) {
      return;
    }

    let active = true;

    async function load() {
      try {
        const roi =
          await getDecisionROI(
            DEFAULT_DECISION_ID
          );

        if (!active) return;

        const recId =
          roi.recommendation_id;

        setWorkflows(
          current => ({
            ...current,

            [recId]: {
              ...(
                current[recId] ||
                {}
              ),

              decision: {
                ...(
                  current[recId]
                    ?.decision ||
                  {}
                ),

                decision_id:
                  DEFAULT_DECISION_ID,

                recommendation_id:
                  recId,

                decision_status:
                  "ACCEPTED",

                execution_status:
                  "EXECUTED",
              },

              outcome: {
                outcome_id:
                  roi.outcome_id,

                actual_intervention_cost:
                  roi.actual_intervention_cost,

                actual_delay_cost:
                  roi.actual_delay_cost,

                actual_total_cost:
                  roi.actual_total_cost,

                actual_time_days:
                  roi.actual_time_days,

                actual_delayed:
                  roi.actual_delayed,
              },

              roi,
            },
          })
        );
      } catch {
        // Fresh DBs are allowed to have no completed outcome.
      }
    }

    load();

    return () => {
      active = false;
    };
  }, [
    backend.online,
    refreshKey,
  ]);


  const recommendations =
    useMemo(
      () =>
        optimization.recommendations
          .map(mapRecommendation),
      [
        optimization.recommendations,
      ]
    );


  const history =
    useMemo(
      () =>
        recommendations.map(
          option => {
            const workflow =
              workflows[
                option.recommendationId
              ] || {};

            const decision =
              workflow.decision;

            const roi =
              workflow.roi;

            let outcome =
              "Pending";

            if (
              decision?.decision_status ===
              "REJECTED"
            ) {
              outcome = "Rejected";
            } else if (roi) {
              outcome =
                roi.actual_delayed
                  ? "Delayed"
                  : "On Time";
            } else if (
              decision?.execution_status ===
              "EXECUTED"
            ) {
              outcome =
                "Awaiting Outcome";
            } else if (
              decision?.decision_status ===
              "ACCEPTED"
            ) {
              outcome =
                "Accepted";
            }

            return {
              id:
                option.recommendationId,

              date:
                formatDate(
                  decision?.decided_at ||
                  option.createdAt
                ),

              option:
                option.title,

              predicted:
                option.optimizedCost,

              actual:
                roi
                  ? Number(
                      roi.actual_total_cost
                    )
                  : null,

              outcome,

              status:
                decision?.execution_status ||
                decision?.decision_status ||
                "Recommended",

              workflow,
            };
          }
        ),
      [
        recommendations,
        workflows,
      ]
    );


  function updateWorkflow(
    recommendationId,
    patch
  ) {
    setWorkflows(
      current => ({
        ...current,

        [recommendationId]: {
          ...(
            current[
              recommendationId
            ] || {}
          ),

          ...patch,
        },
      })
    );
  }


  function refreshData() {
    setRefreshKey(
      value => value + 1
    );

    showToast(
      "Refreshing FastAPI/PostgreSQL data.",
      "info"
    );
  }


  // ==========================================================
  // RUN REAL OPTIMIZER
  // ==========================================================

  async function runOptimization() {
    if (
      !dashboard.prediction ||
      !dashboard.order
    ) {
      showToast(
        "A persisted ML prediction is required.",
        "error"
      );

      return;
    }

    setOptimizerBusy(true);

    try {
      const prediction =
        dashboard.prediction;

      const order =
        dashboard.order;

      const result =
        await optimize({
          request_id:
            `frontend-${Date.now()}`,

          shipments: [
            {
              shipment_id:
                `ORDER-${order.order_id}`,

              late_probability:
                Number(
                  prediction
                    .late_risk_probability
                ),

              late_penalty:
                Number(
                  constraints
                    .latePenalty
                ),

              baseline_time_days:
                Number(
                  constraints
                    .baselineTimeDays
                ),

              expedite_available:
                constraints
                  .expediteAvailable,

              priority_available:
                constraints
                  .priorityAvailable,

              route_available:
                constraints
                  .routeAvailable,

              hub_available:
                constraints
                  .hubAvailable,
            },
          ],

          constraints: {
            total_budget:
              Number(
                constraints
                  .totalBudget
              ),

            expedite_capacity:
              Number(
                constraints
                  .expediteCapacity
              ),

            priority_capacity:
              Number(
                constraints
                  .priorityCapacity
              ),

            route_capacity:
              Number(
                constraints
                  .routeCapacity
              ),

            hub_capacity:
              Number(
                constraints
                  .hubCapacity
              ),
          },

          prediction_ids: [
            prediction.prediction_id,
          ],
        });


      const recId =
        result.recommendation_ids
          ?.find(Boolean);

      if (!recId) {
        throw new Error(
          "No persisted recommendation ID returned."
        );
      }


      const rec =
        await getRecommendation(
          recId
        );


      const data =
        await getRunRecommendations(
          rec.run_id
        );


      setCurrentRunId(
        rec.run_id
      );

      setOptimization({
        loading: false,
        error: null,
        run:
          data.run ?? null,
        recommendations:
          data.recommendations ??
          [],
      });


      setSelectedId(
        recId
      );


      showToast(
        `Optimization Run #${rec.run_id} persisted.`,
        "success"
      );

      setPage(
        "dashboard"
      );
    } catch (error) {
      showToast(
        error.message,
        "error"
      );
    } finally {
      setOptimizerBusy(false);
    }
  }


  // ==========================================================
  // DECISION
  // ==========================================================

  async function makeDecision(
    option,
    status
  ) {
    try {
      const decision =
        await createDecision(
          option.recommendationId,
          {
            decision_status:
              status,

            decided_by:
              "frontend-ui",

            decision_note:
              `${status} from SupplyPrescript dashboard`,
          }
        );


      updateWorkflow(
        option.recommendationId,
        {
          decision,
          outcome: null,
          roi: null,
        }
      );


      setSelectedId(
        option.recommendationId
      );


      showToast(
        status === "ACCEPTED"
          ? `${option.title} accepted.`
          : `${option.title} rejected.`,
        status === "ACCEPTED"
          ? "success"
          : "info"
      );
    } catch (error) {
      showToast(
        error.message,
        "error"
      );
    }
  }


  // ==========================================================
  // EXECUTION
  // ==========================================================

  async function executeOption(option) {
    const decision =
      workflows[
        option.recommendationId
      ]?.decision;

    if (!decision?.decision_id) {
      showToast(
        "Accept the recommendation first.",
        "error"
      );

      return;
    }


    try {
      const result =
        await executeDecision(
          decision.decision_id
        );


      updateWorkflow(
        option.recommendationId,
        {
          decision: result,
        }
      );


      setOutcomeTarget(
        option
      );


      showToast(
        `${option.title} executed.`,
        "success"
      );
    } catch (error) {
      showToast(
        error.message,
        "error"
      );
    }
  }


  // ==========================================================
  // OUTCOME + ROI
  // ==========================================================

  async function saveOutcome(
    option,
    payload
  ) {
    const decision =
      workflows[
        option.recommendationId
      ]?.decision;

    if (!decision?.decision_id) {
      showToast(
        "No executed decision found.",
        "error"
      );

      return;
    }


    try {
      const outcome =
        await recordOutcome(
          decision.decision_id,
          payload
        );


      const roi =
        await getDecisionROI(
          decision.decision_id
        );


      updateWorkflow(
        option.recommendationId,
        {
          outcome,
          roi,
        }
      );


      setOutcomeTarget(null);


      showToast(
        "Outcome saved and ROI calculated.",
        "success"
      );
    } catch (error) {
      showToast(
        error.message,
        "error"
      );
    }
  }


  return (
    <div className="app">

      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            SP
          </div>

          <div>
            <h1>
              SupplyPrescript
            </h1>

            <span>
              Closed-Loop Analytics
            </span>
          </div>
        </div>


        <nav>
          <NavButton
            active={
              page === "dashboard"
            }
            icon="▦"
            text="Dashboard"
            onClick={() =>
              setPage("dashboard")
            }
          />

          <NavButton
            active={
              page === "decisions"
            }
            icon="✓"
            text="Decisions"
            onClick={() =>
              setPage("decisions")
            }
          />

          <NavButton
            active={
              page === "analytics"
            }
            icon="◔"
            text="Decision ROI"
            onClick={() =>
              setPage("analytics")
            }
          />

          <NavButton
            active={
              page === "settings"
            }
            icon="⚙"
            text="Constraints"
            onClick={() =>
              setPage("settings")
            }
          />
        </nav>


        <div className="sidebar-bottom">
          <div className="system-status">
            <span
              className={`dot ${
                backend.checking
                  ? "checking"
                  : backend.online
                  ? "online"
                  : "offline"
              }`}
            />

            <div>
              <strong>
                {backend.checking
                  ? "Checking System"
                  : backend.online
                  ? "System Online"
                  : "System Offline"}
              </strong>

              <small>
                {backend.checking
                  ? "Connecting to FastAPI..."
                  : backend.online
                  ? backend.modelsLoaded
                    ? `SupplyPrescript ML V2${
                        backend.threshold !==
                        null
                          ? ` • Threshold ${Number(
                              backend.threshold
                            ).toFixed(2)}`
                          : ""
                      }`
                    : "Backend ready • Model loading"
                  : "Backend unavailable"}
              </small>
            </div>
          </div>


          <button
            className="reset-btn"
            onClick={
              refreshData
            }
          >
            Refresh Data
          </button>
        </div>
      </aside>


      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              OPERATIONS CONTROL CENTER
            </p>

            <h2>
              {page === "dashboard"
                ? "Supply Chain Command Center"
                : page === "decisions"
                ? "Decision History"
                : page === "analytics"
                ? "Decision ROI & Feedback"
                : "Optimization Constraints"}
            </h2>
          </div>

          <div className="header-right">
            <span className="live">
              <span
                className={`dot ${
                  backend.online
                    ? "online"
                    : "offline"
                }`}
              />

              Live monitoring
            </span>

            <div className="avatar">
              LM
            </div>
          </div>
        </header>


        {page === "dashboard" && (
          <Dashboard
            dashboard={
              dashboard
            }
            optimization={
              optimization
            }
            recommendations={
              recommendations
            }
            workflows={
              workflows
            }
            selectedId={
              selectedId
            }
            outcomeTarget={
              outcomeTarget
            }
            budget={
              Number(
                constraints
                  .totalBudget
              )
            }
            onSelect={
              setSelectedId
            }
            onAccept={
              option =>
                makeDecision(
                  option,
                  "ACCEPTED"
                )
            }
            onReject={
              option =>
                makeDecision(
                  option,
                  "REJECTED"
                )
            }
            onExecute={
              executeOption
            }
            onOpenOutcome={
              setOutcomeTarget
            }
            onSaveOutcome={
              saveOutcome
            }
            onCancelOutcome={() =>
              setOutcomeTarget(null)
            }
            onPage={
              setPage
            }
          />
        )}


        {page === "decisions" && (
          <Decisions
            rows={
              history
            }
          />
        )}


        {page === "analytics" && (
          <Analytics
            rows={
              history
            }
          />
        )}


        {page === "settings" && (
          <Settings
            constraints={
              constraints
            }
            setConstraints={
              setConstraints
            }
            onRun={
              runOptimization
            }
            busy={
              optimizerBusy
            }
            predictionAvailable={
              Boolean(
                dashboard.prediction
              )
            }
          />
        )}


        <ToastContainer
          toasts={
            toasts
          }
          onDismiss={
            dismissToast
          }
        />
      </main>
    </div>
  );
}


// ============================================================
// NAV
// ============================================================

function NavButton({
  active,
  icon,
  text,
  onClick,
}) {
  return (
    <button
      className={
        active
          ? "nav active"
          : "nav"
      }
      onClick={
        onClick
      }
    >
      <span>
        {icon}
      </span>

      {text}
    </button>
  );
}


// ============================================================
// DASHBOARD
// ============================================================

function Dashboard({
  dashboard,
  optimization,
  recommendations,
  workflows,
  selectedId,
  outcomeTarget,
  budget,
  onSelect,
  onAccept,
  onReject,
  onExecute,
  onOpenOutcome,
  onSaveOutcome,
  onCancelOutcome,
  onPage,
}) {
  const prediction =
    dashboard.prediction;

  const order =
    dashboard.order;

  const risk =
    prediction
      ?.late_risk_probability !=
    null
      ? Number(
          prediction
            .late_risk_probability
        ) * 100
      : null;

  const threshold =
    prediction
      ?.threshold_used !=
    null
      ? Number(
          prediction.threshold_used
        ) * 100
      : null;

  const highRisk =
    prediction
      ?.predicted_late_risk ===
    true;

  const executed =
    recommendations.some(
      option =>
        workflows[
          option.recommendationId
        ]?.decision
          ?.execution_status ===
        "EXECUTED"
    );

  const measured =
    recommendations.some(
      option =>
        Boolean(
          workflows[
            option.recommendationId
          ]?.roi
        )
    );


  return (
    <div className="content">

      <section className="alert-banner">
        <div className="alert-icon">
          !
        </div>

        <div className="alert-text">
          <strong>
            {dashboard.loading
              ? "Loading Supply Chain Risk"
              : dashboard.error
              ? "Prediction Data Unavailable"
              : highRisk
              ? "Critical Supply Chain Risk Detected"
              : "Shipment Risk Within Threshold"}
          </strong>

          <span>
            {dashboard.loading
              ? "Retrieving latest ML prediction..."
              : dashboard.error
              ? dashboard.error
              : `Order #${
                  order?.order_id ??
                  "—"
                } has ${
                  highRisk
                    ? "an elevated late-delivery risk."
                    : "a low predicted late-delivery risk."
                }`}
          </span>
        </div>

        <div className="risk-probability">
          <span>
            Late-risk probability
          </span>

          <b>
            {risk === null
              ? "—"
              : percent(risk)}
          </b>
        </div>
      </section>


      <section className="metric-grid">
        <Metric
          label="Order"
          value={
            order?.order_id
              ? `#${order.order_id}`
              : "—"
          }
          note={
            order?.order_status ??
            "Awaiting data"
          }
        />

        <Metric
          label="Late Risk"
          value={
            risk === null
              ? "—"
              : percent(risk)
          }
          note={
            highRisk
              ? "High-risk prediction"
              : "Low-risk prediction"
          }
          danger={
            highRisk
          }
        />

        <Metric
          label="Budget Available"
          value={
            money(budget)
          }
          note="Optimization limit"
        />

        <Metric
          label="ML Threshold"
          value={
            threshold === null
              ? "—"
              : percent(
                  threshold,
                  0
                )
          }
          note="SupplyPrescript ML V2"
        />
      </section>


      <section className="section-heading">
        <div>
          <p className="eyebrow">
            PRESCRIPTIVE ENGINE
          </p>

          <h3>
            What should we do?
          </h3>

          <p className="muted">
            PuLP evaluates intervention cost,
            expected loss, capacities and
            operational risk.
          </p>
        </div>

        <div className="solver-badge">
          ✓ PuLP / CBC •{" "}
          {optimization.run
            ?.optimization_status ||
            "Waiting"}
        </div>
      </section>


      <section className="recommendations real-recommendations">
        {optimization.loading ? (
          <div className="card integration-state">
            Loading optimizer recommendation...
          </div>
        ) : optimization.error ? (
          <div className="card integration-state error-state">
            {optimization.error}
          </div>
        ) : recommendations.length ===
          0 ? (
          <div className="card integration-state">
            No recommendation is available.
            Run the optimizer from Constraints.
          </div>
        ) : (
          recommendations.map(
            option => (
              <RecommendationCard
                key={
                  option.recommendationId
                }
                option={
                  option
                }
                workflow={
                  workflows[
                    option.recommendationId
                  ] || {}
                }
                selected={
                  selectedId ===
                  option.recommendationId
                }
                budget={
                  budget
                }
                onSelect={
                  onSelect
                }
                onAccept={
                  onAccept
                }
                onReject={
                  onReject
                }
                onExecute={
                  onExecute
                }
                onOpenOutcome={
                  onOpenOutcome
                }
              />
            )
          )
        )}
      </section>


      {outcomeTarget && (
        <OutcomeForm
          option={
            outcomeTarget
          }
          onSubmit={
            payload =>
              onSaveOutcome(
                outcomeTarget,
                payload
              )
          }
          onCancel={
            onCancelOutcome
          }
        />
      )}


      <section className="workflow">
        <div className="section-heading compact">
          <div>
            <p className="eyebrow">
              CLOSED LOOP
            </p>

            <h3>
              Decision workflow
            </h3>
          </div>
        </div>

        <div className="steps">
          <Step
            number="01"
            title="Predict"
            text={
              risk === null
                ? "Waiting for ML prediction."
                : `ML ensemble detects ${percent(
                    risk
                  )} late risk.`
            }
            done={
              Boolean(prediction)
            }
          />

          <div className="connector" />

          <Step
            number="02"
            title="Prescribe"
            text={
              recommendations.length
                ? `PuLP persisted ${recommendations.length} recommendation(s).`
                : "Waiting for optimizer."
            }
            done={
              recommendations.length >
              0
            }
          />

          <div className="connector" />

          <Step
            number="03"
            title="Execute"
            text={
              executed
                ? "Accepted decision executed."
                : "Accept or reject an intervention."
            }
            done={
              executed
            }
          />

          <div className="connector" />

          <Step
            number="04"
            title="Measure"
            text={
              measured
                ? "Outcome recorded and ROI calculated."
                : "Record actual outcome after execution."
            }
            done={
              measured
            }
          />
        </div>

        <button
          className="outline-btn"
          onClick={() =>
            onPage("decisions")
          }
        >
          View Decision History →
        </button>
      </section>
    </div>
  );
}


// ============================================================
// RECOMMENDATION
// ============================================================

function RecommendationCard({
  option,
  workflow,
  selected,
  budget,
  onSelect,
  onAccept,
  onReject,
  onExecute,
  onOpenOutcome,
}) {
  const decision =
    workflow.decision;

  const roi =
    workflow.roi;

  const rejected =
    decision?.decision_status ===
    "REJECTED";

  const accepted =
    decision?.decision_status ===
    "ACCEPTED";

  const executed =
    decision?.execution_status ===
    "EXECUTED";

  const overBudget =
    option.cost >
    budget;


  let label =
    "Accept Recommendation";

  let disabled =
    false;

  let action =
    () =>
      onAccept(option);


  if (rejected) {
    label =
      "Recommendation Rejected";

    disabled = true;
  } else if (roi) {
    label =
      "✓ Outcome Recorded";

    disabled = true;
  } else if (
    accepted &&
    executed
  ) {
    label =
      "Record Actual Outcome";

    action =
      () =>
        onOpenOutcome(option);
  } else if (accepted) {
    label =
      "Execute Decision";

    action =
      () =>
        onExecute(option);
  } else if (overBudget) {
    label =
      "Over Budget";

    disabled = true;
  }


  return (
    <article
      className={`recommendation card ${
        selected
          ? "selected"
          : ""
      } ${
        executed
          ? "executed"
          : ""
      }`}
    >
      <div className="card-top">
        <div className="option-letter">
          {option.id}
        </div>

        <div>
          <div className="title-line">
            <h4>
              {option.title}
            </h4>

            <span className="tag">
              {option.tag}
            </span>
          </div>

          <p>
            {option.description}
          </p>
        </div>
      </div>


      <div className="score">
        <div className="score-ring">
          <b>
            {option.score}
          </b>

          <span>%</span>
        </div>

        <div>
          <small>
            Relative risk reduction
          </small>

          <div className="progress">
            <span
              style={{
                width:
                  `${option.score}%`,
              }}
            />
          </div>
        </div>
      </div>


      <div className="option-metrics">
        <div>
          <span>
            Action cost
          </span>

          <b>
            {money(option.cost)}
          </b>
        </div>

        <div>
          <span>
            Predicted time
          </span>

          <b>
            {option.days === null
              ? "—"
              : `${option.days} days`}
          </b>
        </div>

        <div>
          <span>
            Risk after
          </span>

          <b>
            {percent(
              option.riskAfter *
                100
            )}
          </b>
        </div>
      </div>


      <div className="tradeoffs">
        <div>
          <strong>
            Advantages
          </strong>

          {option.pros.map(
            item => (
              <span key={item}>
                ✓ {item}
              </span>
            )
          )}
        </div>

        <div>
          <strong>
            Trade-offs
          </strong>

          {option.cons.map(
            item => (
              <span key={item}>
                • {item}
              </span>
            )
          )}
        </div>
      </div>


      {roi && (
        <div className="roi-mini">
          <span>
            Model-relative realized ROI
          </span>

          <strong>
            {percent(
              roi.realized_roi_percent
            )}
          </strong>
        </div>
      )}


      <div className="recommendation-actions">
        <button
          className="execute-btn"
          disabled={
            disabled
          }
          onClick={
            action
          }
        >
          {label}
        </button>


        {!decision && (
          <button
            className="outline-btn danger-outline"
            onClick={() =>
              onReject(option)
            }
          >
            Reject
          </button>
        )}
      </div>


      <button
        className="select-link"
        onClick={() =>
          onSelect(
            option.recommendationId
          )
        }
      >
        {selected
          ? "Selected for review"
          : "Review recommendation"}
      </button>
    </article>
  );
}


// ============================================================
// OUTCOME
// ============================================================

function OutcomeForm({
  option,
  onSubmit,
  onCancel,
}) {
  const [
    saving,
    setSaving,
  ] = useState(false);

  const [
    form,
    setForm,
  ] = useState({
    actual_intervention_cost:
      option.cost,

    actual_time_days:
      option.days ?? 0,

    actual_delayed:
      false,

    actual_delay_cost:
      0,

    outcome_note:
      "",
  });


  function change(
    key,
    value
  ) {
    setForm(
      current => ({
        ...current,
        [key]: value,
      })
    );
  }


  async function submit(event) {
    event.preventDefault();

    setSaving(true);

    try {
      await onSubmit({
        actual_intervention_cost:
          Number(
            form
              .actual_intervention_cost
          ),

        actual_time_days:
          Number(
            form.actual_time_days
          ),

        actual_delayed:
          Boolean(
            form.actual_delayed
          ),

        actual_delay_cost:
          Number(
            form.actual_delay_cost
          ),

        outcome_note:
          form.outcome_note ||
          null,
      });
    } finally {
      setSaving(false);
    }
  }


  return (
    <section className="card outcome-panel">
      <div className="table-head">
        <div>
          <p className="eyebrow">
            ACTUAL OUTCOME
          </p>

          <h3>
            Record result for{" "}
            {option.title}
          </h3>
        </div>
      </div>


      <form
        className="outcome-form"
        onSubmit={
          submit
        }
      >
        <NumberInput
          label="Actual intervention cost"
          value={
            form
              .actual_intervention_cost
          }
          step="0.01"
          onChange={
            value =>
              change(
                "actual_intervention_cost",
                value
              )
          }
        />

        <NumberInput
          label="Actual time (days)"
          value={
            form.actual_time_days
          }
          step="0.01"
          onChange={
            value =>
              change(
                "actual_time_days",
                value
              )
          }
        />

        <NumberInput
          label="Actual delay cost"
          value={
            form.actual_delay_cost
          }
          step="0.01"
          onChange={
            value =>
              change(
                "actual_delay_cost",
                value
              )
          }
        />


        <label className="checkbox-field">
          <input
            type="checkbox"
            checked={
              form.actual_delayed
            }
            onChange={
              event =>
                change(
                  "actual_delayed",
                  event.target.checked
                )
            }
          />

          <span>
            Shipment was actually delayed
          </span>
        </label>


        <label className="full-field">
          <span>
            Outcome note
          </span>

          <input
            type="text"
            value={
              form.outcome_note
            }
            onChange={
              event =>
                change(
                  "outcome_note",
                  event.target.value
                )
            }
          />
        </label>


        <div className="outcome-actions full-field">
          <button
            className="primary-btn"
            type="submit"
            disabled={
              saving
            }
          >
            {saving
              ? "Saving..."
              : "Save Outcome & Calculate ROI"}
          </button>

          <button
            className="outline-btn"
            type="button"
            onClick={
              onCancel
            }
          >
            Cancel
          </button>
        </div>
      </form>
    </section>
  );
}


// ============================================================
// DECISIONS
// ============================================================

function Decisions({
  rows,
}) {
  return (
    <div className="content">
      <div className="page-card card">
        <div className="table-head">
          <div>
            <p className="eyebrow">
              POSTGRESQL WRITE-BACK
            </p>

            <h3>
              Operational Decisions
            </h3>
          </div>

          <span className="count">
            {rows.length} records
          </span>
        </div>


        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Action</th>
                <th>
                  Predicted Cost
                </th>
                <th>
                  Actual Cost
                </th>
                <th>Outcome</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {rows.map(
                row => (
                  <tr key={row.id}>
                    <td>
                      {row.date}
                    </td>

                    <td>
                      <b>
                        {row.option}
                      </b>
                    </td>

                    <td>
                      {money(
                        row.predicted
                      )}
                    </td>

                    <td>
                      {row.actual ===
                      null
                        ? "Pending"
                        : money(
                            row.actual
                          )}
                    </td>

                    <td>
                      {row.outcome}
                    </td>

                    <td>
                      {row.status}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>


        <div className="info-box">
          Decisions, executions and outcomes are now written through FastAPI to PostgreSQL. Browser storage only retains returned backend IDs for the current UI session/history.
        </div>
      </div>
    </div>
  );
}


// ============================================================
// ANALYTICS
// ============================================================

function Analytics({
  rows,
}) {
  const completed =
    rows.filter(
      row =>
        row.actual !== null
    );

  const latestROI =
    [...rows]
      .reverse()
      .find(
        row =>
          row.workflow?.roi
      )
      ?.workflow?.roi ||
    null;

  const avgPredicted =
    rows.length
      ? rows.reduce(
          (
            total,
            row
          ) =>
            total +
            Number(
              row.predicted || 0
            ),
          0
        ) / rows.length
      : 0;

  const avgActual =
    completed.length
      ? completed.reduce(
          (
            total,
            row
          ) =>
            total +
            Number(
              row.actual || 0
            ),
          0
        ) / completed.length
      : 0;

  const max =
    Math.max(
      ...rows.flatMap(
        row => [
          Number(
            row.predicted || 0
          ),
          Number(
            row.actual || 0
          ),
        ]
      ),
      1
    );


  return (
    <div className="content">
      <section className="metric-grid analytics-grid">
        <Metric
          label="Decisions Tracked"
          value={
            rows.filter(
              row =>
                row.workflow?.decision
            ).length
          }
          note="Closed-loop records"
        />

        <Metric
          label="Completed Outcomes"
          value={
            completed.length
          }
          note="Actual results recorded"
        />

        <Metric
          label="Avg Predicted Cost"
          value={
            money(avgPredicted)
          }
          note="Optimized expected cost"
        />

        <Metric
          label="Avg Actual Cost"
          value={
            completed.length
              ? money(avgActual)
              : "—"
          }
          note="Recorded result"
        />
      </section>


      <div className="analytics-layout">
        <section className="card chart-card">
          <p className="eyebrow">
            COST FEEDBACK
          </p>

          <h3>
            Predicted vs Actual Cost
          </h3>

          <div className="bars">
            {rows.map(
              row => (
                <div
                  className="bar-group"
                  key={row.id}
                >
                  <div className="bar-set">
                    <div
                      className="bar predicted"
                      style={{
                        height:
                          `${
                            (
                              row.predicted /
                              max
                            ) *
                            150
                          }px`,
                      }}
                    />

                    {row.actual !==
                      null && (
                      <div
                        className="bar actual"
                        style={{
                          height:
                            `${
                              (
                                row.actual /
                                max
                              ) *
                              150
                            }px`,
                        }}
                      />
                    )}
                  </div>

                  <small>
                    {row.option}
                  </small>
                </div>
              )
            )}
          </div>

          <div className="legend">
            <span>
              <i className="legend-box predicted" />
              Predicted
            </span>

            <span>
              <i className="legend-box actual" />
              Actual
            </span>
          </div>
        </section>


        <section className="card learning-card">
          <p className="eyebrow">
            CLOSED-LOOP FEEDBACK
          </p>

          <h3>
            Outcome & ROI
          </h3>

          <div className="learning-flow">
            <div>
              <b>1</b>
              <span>
                Recommendation persisted
              </span>
            </div>

            <div>
              <b>2</b>
              <span>
                Decision executed
              </span>
            </div>

            <div>
              <b>3</b>
              <span>
                Actual outcome recorded
              </span>
            </div>

            <div>
              <b>4</b>
              <span>
                ROI calculated
              </span>
            </div>
          </div>


          {latestROI ? (
            <div className="roi-summary">
              <div>
                <span>
                  Selected action
                </span>

                <strong>
                  {prettyAction(
                    latestROI
                      .selected_action
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Model-relative ROI
                </span>

                <strong>
                  {percent(
                    latestROI
                      .realized_roi_percent
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Savings vs baseline
                </span>

                <strong>
                  {money(
                    latestROI
                      .realized_savings_vs_baseline
                  )}
                </strong>
              </div>

              <div>
                <span>
                  Time variance
                </span>

                <strong>
                  {Number(
                    latestROI
                      .time_variance_days ||
                    0
                  ).toFixed(2)} days
                </strong>
              </div>
            </div>
          ) : (
            <div className="model-status">
              <span className="dot" />
              Record an actual outcome to calculate ROI.
            </div>
          )}
        </section>
      </div>
    </div>
  );
}


// ============================================================
// SETTINGS
// ============================================================

function Settings({
  constraints,
  setConstraints,
  onRun,
  busy,
  predictionAvailable,
}) {
  function update(
    key,
    value
  ) {
    setConstraints(
      current => ({
        ...current,
        [key]: value,
      })
    );
  }


  return (
    <div className="content">
      <section className="settings-card card">
        <p className="eyebrow">
          OPTIMIZATION RULES
        </p>

        <h3>
          Business Constraints
        </h3>

        <p className="muted">
          These settings are sent directly to the real PuLP/CBC optimizer. Running it persists a new optimization run and recommendation in PostgreSQL.
        </p>


        <div className="form-grid">
          <NumberInput
            label="Total budget ($)"
            value={
              constraints.totalBudget
            }
            onChange={
              value =>
                update(
                  "totalBudget",
                  value
                )
            }
          />

          <NumberInput
            label="Late penalty ($)"
            value={
              constraints.latePenalty
            }
            onChange={
              value =>
                update(
                  "latePenalty",
                  value
                )
            }
          />

          <NumberInput
            label="Baseline time (days)"
            value={
              constraints.baselineTimeDays
            }
            step="0.1"
            onChange={
              value =>
                update(
                  "baselineTimeDays",
                  value
                )
            }
          />

          <NumberInput
            label="Expedite capacity"
            value={
              constraints.expediteCapacity
            }
            onChange={
              value =>
                update(
                  "expediteCapacity",
                  value
                )
            }
          />

          <NumberInput
            label="Priority capacity"
            value={
              constraints.priorityCapacity
            }
            onChange={
              value =>
                update(
                  "priorityCapacity",
                  value
                )
            }
          />

          <NumberInput
            label="Route capacity"
            value={
              constraints.routeCapacity
            }
            onChange={
              value =>
                update(
                  "routeCapacity",
                  value
                )
            }
          />

          <NumberInput
            label="Hub capacity"
            value={
              constraints.hubCapacity
            }
            onChange={
              value =>
                update(
                  "hubCapacity",
                  value
                )
            }
          />
        </div>


        <div className="availability-grid">
          <CheckInput
            text="Expedite available"
            checked={
              constraints
                .expediteAvailable
            }
            onChange={
              value =>
                update(
                  "expediteAvailable",
                  value
                )
            }
          />

          <CheckInput
            text="Priority available"
            checked={
              constraints
                .priorityAvailable
            }
            onChange={
              value =>
                update(
                  "priorityAvailable",
                  value
                )
            }
          />

          <CheckInput
            text="Alternative route available"
            checked={
              constraints
                .routeAvailable
            }
            onChange={
              value =>
                update(
                  "routeAvailable",
                  value
                )
            }
          />

          <CheckInput
            text="Alternative hub available"
            checked={
              constraints
                .hubAvailable
            }
            onChange={
              value =>
                update(
                  "hubAvailable",
                  value
                )
            }
          />
        </div>


        <button
          className="primary-btn"
          disabled={
            busy ||
            !predictionAvailable
          }
          onClick={
            onRun
          }
        >
          {busy
            ? "Running Optimizer..."
            : predictionAvailable
            ? "Run & Persist Optimization"
            : "Waiting for Prediction"}
        </button>
      </section>
    </div>
  );
}


// ============================================================
// SMALL COMPONENTS
// ============================================================

function Metric({
  label,
  value,
  note,
  danger,
}) {
  return (
    <div className="metric card">
      <span>
        {label}
      </span>

      <strong
        className={
          danger
            ? "danger-text"
            : ""
        }
      >
        {value}
      </strong>

      <small>
        {note}
      </small>
    </div>
  );
}


function Step({
  number,
  title,
  text,
  done,
}) {
  return (
    <div
      className={`step ${
        done ? "done" : ""
      }`}
    >
      <div className="step-number">
        {done
          ? "✓"
          : number}
      </div>

      <strong>
        {title}
      </strong>

      <span>
        {text}
      </span>
    </div>
  );
}


function NumberInput({
  label,
  value,
  onChange,
  step = "1",
}) {
  return (
    <label>
      <span>
        {label}
      </span>

      <input
        type="number"
        min="0"
        step={step}
        value={value}
        onChange={
          event =>
            onChange(
              Number(
                event.target.value
              )
            )
        }
      />
    </label>
  );
}


function CheckInput({
  text,
  checked,
  onChange,
}) {
  return (
    <label className="availability-item">
      <input
        type="checkbox"
        checked={checked}
        onChange={
          event =>
            onChange(
              event.target.checked
            )
        }
      />

      <span>
        {text}
      </span>
    </label>
  );
}


// ============================================================
// ROOT
// ============================================================

createRoot(
  document.getElementById("root")
).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);