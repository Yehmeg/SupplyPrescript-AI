import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/components.css";
import "./styles/layout.css";
import "./styles/legacy.css";
import { initialRecommendations, initialHistory } from "./data/mockData";
import { useDecisionHistory } from "./hooks/useDecisionHistory";
import { useToast } from "./hooks/useToast";
import { ToastContainer } from "./components/ui/Toast";
import { ErrorBoundary } from "./components/ui/ErrorBoundary";

function App() {
  const [page, setPage] = useState("dashboard");
  const [recommendations] = useState(initialRecommendations);
  const [selected, setSelected] = useState(null);
  const [executed, setExecuted] = useState(null);
  const [budget, setBudget] = useState(20000);
  const [inventory, setInventory] = useState(250);

  const { history, stats, addDecision, resetHistory } = useDecisionHistory();
  const { toasts, showToast, dismissToast } = useToast();

  function executeDecision(option) {
    if (option.cost > budget) {
      showToast("This recommendation violates the current budget.", "error");
      return;
    }
    setSelected(option);
    setExecuted(option);
    addDecision(option);
    showToast(`Option ${option.id} executed successfully. Decision written to operational log.`, "success");
  }

  function resetDemo() {
    resetHistory();
    setExecuted(null);
    setSelected(null);
    showToast("Demo data reset.", "info");
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">SP</div>
          <div>
            <h1>SupplyPrescript</h1>
            <span>Closed-Loop Analytics</span>
          </div>
        </div>

        <nav>
          <button className={page === "dashboard" ? "nav active" : "nav"} onClick={() => setPage("dashboard")}>
            <span>▦</span> Dashboard
          </button>
          <button className={page === "decisions" ? "nav active" : "nav"} onClick={() => setPage("decisions")}>
            <span>✓</span> Decisions
          </button>
          <button className={page === "analytics" ? "nav active" : "nav"} onClick={() => setPage("analytics")}>
            <span>◔</span> Decision ROI
          </button>
          <button className={page === "settings" ? "nav active" : "nav"} onClick={() => setPage("settings")}>
            <span>⚙</span> Constraints
          </button>
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="dot"></span>
            <div>
              <strong>System Online</strong>
              <small>Model v1.0 • Ready</small>
            </div>
          </div>
          <button className="reset-btn" onClick={resetDemo}>Reset Demo</button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">OPERATIONS CONTROL CENTER</p>
            <h2>{page === "dashboard" ? "Supply Chain Command Center" : page === "decisions" ? "Decision History" : page === "analytics" ? "Decision ROI & Feedback" : "Optimization Constraints"}</h2>
          </div>
          <div className="header-right">
            <span className="live"><span className="dot"></span> Live monitoring</span>
            <div className="avatar">LM</div>
          </div>
        </header>

        {page === "dashboard" && (
          <Dashboard
            recommendations={recommendations}
            selected={selected}
            executed={executed}
            budget={budget}
            inventory={inventory}
            onSelect={setSelected}
            onExecute={executeDecision}
            onPage={setPage}
          />
        )}

        {page === "decisions" && <Decisions history={history} />}
        {page === "analytics" && <Analytics stats={stats} history={history} />}
        {page === "settings" && (
          <Settings
            budget={budget}
            setBudget={setBudget}
            inventory={inventory}
            setInventory={setInventory}
            onSave={() => showToast("Optimization constraints saved for this demo.")}
          />
        )}

        <ToastContainer toasts={toasts} onDismiss={dismissToast} />
      </main>
    </div>
  );
}

function Dashboard({ recommendations, selected, executed, budget, inventory, onSelect, onExecute, onPage }) {
  return (
    <div className="content">
      <section className="alert-banner">
        <div className="alert-icon">!</div>
        <div className="alert-text">
          <strong>Critical Supply Chain Risk Detected</strong>
          <span>Microchip shipment <b>MC-2048</b> has a predicted <b>14-day delay</b>.</span>
        </div>
        <div className="risk-probability">
          <span>Delay probability</span>
          <b>91%</b>
        </div>
      </section>

      <section className="metric-grid">
        <Metric label="Shipment" value="MC-2048" note="Microchips" />
        <Metric label="Predicted Delay" value="14 days" note="XGBoost forecast" danger />
        <Metric label="Budget Available" value={`$${budget.toLocaleString()}`} note="Optimization limit" />
        <Metric label="Inventory" value={`${inventory} units`} note="Minimum protected" />
      </section>

      <section className="section-heading">
        <div>
          <p className="eyebrow">PRESCRIPTIVE ENGINE</p>
          <h3>What should we do?</h3>
          <p className="muted">The optimization engine evaluated cost, speed, budget and operational risk.</p>
        </div>
        <div className="solver-badge">✓ SciPy Solver • Optimized</div>
      </section>

      <section className="recommendations">
        {recommendations.map(option => (
          <RecommendationCard
            key={option.id}
            option={option}
            selected={selected?.id === option.id}
            executed={executed?.id === option.id}
            budget={budget}
            onSelect={onSelect}
            onExecute={onExecute}
          />
        ))}
      </section>

      <section className="workflow">
        <div className="section-heading compact">
          <div>
            <p className="eyebrow">CLOSED LOOP</p>
            <h3>Decision workflow</h3>
          </div>
        </div>
        <div className="steps">
          <Step number="01" title="Predict" text="XGBoost detects 91% delay risk." done />
          <div className="connector"></div>
          <Step number="02" title="Prescribe" text="Optimization creates 3 actions." done />
          <div className="connector"></div>
          <Step number="03" title="Execute" text={executed ? "Manager executed a decision." : "Manager selects an action."} done={!!executed} />
          <div className="connector"></div>
          <Step number="04" title="Learn" text="Actual outcome feeds the model." />
        </div>
        <button className="outline-btn" onClick={() => onPage("decisions")}>View Decision History →</button>
      </section>
    </div>
  );
}

function Metric({ label, value, note, danger }) {
  return (
    <div className="metric card">
      <span>{label}</span>
      <strong className={danger ? "danger-text" : ""}>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

function RecommendationCard({ option, selected, executed, budget, onSelect, onExecute }) {
  const disabled = option.cost > budget;
  return (
    <article className={`recommendation card ${selected ? "selected" : ""} ${executed ? "executed" : ""}`}>
      <div className="card-top">
        <div className="option-letter">{option.id}</div>
        <div>
          <div className="title-line">
            <h4>{option.title}</h4>
            <span className="tag">{option.tag}</span>
          </div>
          <p>{option.description}</p>
        </div>
      </div>

      <div className="score">
        <div className="score-ring"><b>{option.score}</b><span>score</span></div>
        <div>
          <small>Optimization score</small>
          <div className="progress"><span style={{ width: `${option.score}%` }}></span></div>
        </div>
      </div>

      <div className="option-metrics">
        <div><span>Estimated cost</span><b>${option.cost.toLocaleString()}</b></div>
        <div><span>Recovery time</span><b>{option.deliveryDays} days</b></div>
        <div><span>Risk</span><b>{option.risk}</b></div>
      </div>

      <div className="tradeoffs">
        <div><strong>Advantages</strong>{option.pros.map(x => <span key={x}>✓ {x}</span>)}</div>
        <div><strong>Trade-offs</strong>{option.cons.map(x => <span key={x}>• {x}</span>)}</div>
      </div>

      <button
        className={executed ? "execute-btn done" : "execute-btn"}
        disabled={disabled || executed}
        onClick={() => onExecute(option)}
      >
        {executed ? "✓ Decision Executed" : disabled ? "Over Budget" : `Execute Option ${option.id}`}
      </button>

      <button className="select-link" onClick={() => onSelect(option)}>
        {selected ? "Selected for review" : "Review option"}
      </button>
    </article>
  );
}

function Step({ number, title, text, done }) {
  return (
    <div className={`step ${done ? "done" : ""}`}>
      <div className="step-number">{done ? "✓" : number}</div>
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

function Decisions({ history }) {
  return (
    <div className="content">
      <div className="page-card card">
        <div className="table-head">
          <div>
            <p className="eyebrow">WRITE-BACK LOG</p>
            <h3>Operational Decisions</h3>
          </div>
          <span className="count">{history.length} records</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Date</th><th>Action</th><th>Predicted Cost</th><th>Actual Cost</th><th>Outcome</th><th>Status</th></tr>
            </thead>
            <tbody>
              {history.map(row => (
                <tr key={row.id}>
                  <td>{row.date}</td>
                  <td><b>{row.option}</b></td>
                  <td>${row.predicted.toLocaleString()}</td>
                  <td>{row.actual ? `$${row.actual.toLocaleString()}` : "Pending"}</td>
                  <td><span className={`pill ${row.outcome.toLowerCase()}`}>{row.outcome}</span></td>
                  <td>{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="info-box">
          <b>Frontend demo:</b> clicking Execute Decision currently stores the decision in browser localStorage.
          In the real project this button will call a FastAPI endpoint that performs the database INSERT/write-back.
        </div>
      </div>
    </div>
  );
}

function Analytics({ stats, history }) {
  const max = Math.max(...history.map(x => x.predicted), 1);
  return (
    <div className="content">
      <section className="metric-grid analytics-grid">
        <Metric label="Decisions Tracked" value={stats.total} note="Closed-loop records" />
        <Metric label="Positive Outcomes" value={`${stats.accuracy}%`} note="Outcome success rate" />
        <Metric label="Avg Predicted Cost" value={`$${Math.round(stats.avgPred).toLocaleString()}`} note="Model estimate" />
        <Metric label="Avg Actual Cost" value={`$${Math.round(stats.avgActual).toLocaleString()}`} note="Historical result" />
      </section>

      <div className="analytics-layout">
        <section className="card chart-card">
          <p className="eyebrow">COST FEEDBACK</p>
          <h3>Predicted vs Actual Cost</h3>
          <div className="bars">
            {history.map(row => {
              const actual = row.actual || row.predicted;
              return (
                <div className="bar-group" key={row.id}>
                  <div className="bar-set">
                    <div className="bar predicted" style={{ height: `${(row.predicted / max) * 150}px` }}></div>
                    <div className="bar actual" style={{ height: `${(actual / max) * 150}px` }}></div>
                  </div>
                  <small>{row.option}</small>
                </div>
              );
            })}
          </div>
          <div className="legend"><span><i className="legend-box predicted"></i> Predicted</span><span><i className="legend-box actual"></i> Actual</span></div>
        </section>

        <section className="card learning-card">
          <p className="eyebrow">CONTINUOUS LEARNING</p>
          <h3>Feedback loop</h3>
          <div className="learning-flow">
            <div><b>1</b><span>Decision executed</span></div>
            <div><b>2</b><span>Actual cost recorded</span></div>
            <div><b>3</b><span>Prediction error calculated</span></div>
            <div><b>4</b><span>Model weights updated</span></div>
          </div>
          <div className="model-status"><span className="dot"></span> Next model retraining: after 20 new outcomes</div>
        </section>
      </div>
    </div>
  );
}

function Settings({ budget, setBudget, inventory, setInventory, onSave }) {
  return (
    <div className="content">
      <section className="settings-card card">
        <p className="eyebrow">OPTIMIZATION RULES</p>
        <h3>Business Constraints</h3>
        <p className="muted">These values are used by the prescriptive solver to reject infeasible recommendations.</p>

        <div className="form-grid">
          <label>
            <span>Maximum emergency budget ($)</span>
            <input type="number" value={budget} onChange={e => setBudget(Number(e.target.value))} />
            <small>Example: $20,000 means no recommendation above this amount can be executed.</small>
          </label>
          <label>
            <span>Minimum protected inventory (units)</span>
            <input type="number" value={inventory} onChange={e => setInventory(Number(e.target.value))} />
            <small>The optimization engine must keep at least this inventory level.</small>
          </label>
        </div>

        <div className="constraint-list">
          <div><span>✓</span><b>Budget constraint</b><small>Hard limit</small></div>
          <div><span>✓</span><b>Inventory constraint</b><small>Hard limit</small></div>
          <div><span>✓</span><b>Delivery constraint</b><small>Business priority</small></div>
        </div>

        <button className="primary-btn" onClick={onSave}>Save Constraints</button>
      </section>
    </div>
  );
}

createRoot(document.getElementById("root")).render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);
