# SupplyPrescript Frontend

React + Vite frontend for the **SupplyPrescript** closed-loop prescriptive analytics system. This is the analyst/executive dashboard (React) complementing the Retool operations interface.

## Purpose

Provides an interactive UI for:
- Viewing supply-chain risk alerts and ML-driven delay predictions
- Reviewing prescriptive optimization recommendations (cost/speed/risk trade-offs)
- Executing decisions with audit trail (simulated write-back)
- Analyzing decision ROI and feedback-loop metrics
- Configuring optimization constraints (budget, inventory, delivery limits)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18.3+ (hooks, functional components) |
| Build Tool | Vite 5.4+ |
| Language | JavaScript (ESM) |
| Styling | Plain CSS (CSS custom properties, modular files) |
| State | React hooks (`useState`, `useMemo`, `useEffect`) + custom hooks |
| Persistence | `localStorage` (demo only — no backend yet) |

---

## Folder Structure

```
frontend/
├── index.html                 # Vite entry HTML
├── package.json               # Dependencies & scripts
├── README.md                  # This file
├── src/
│   ├── main.jsx               # App entry, routing, state, all page components
│   ├── data/
│   │   └── mockData.js        # Static demo data (recommendations, history, constraints)
│   ├── hooks/
│   │   ├── useDecisionHistory.js  # localStorage-backed decision log
│   │   ├── useLocalStorage.js     # Generic localStorage hook
│   │   └── useToast.js            # Toast notification system
│   ├── components/
│   │   └── ui/                # Reusable UI primitives
│   │       ├── Button.jsx
│   │       ├── Card.jsx
│   │       ├── Badge.jsx
│   │       ├── Accordion.jsx
│   │       ├── Modal.jsx
│   │       ├── Spinner.jsx
│   │       ├── Toast.jsx
│   │       └── ErrorBoundary.jsx
│   ├── utils/
│   │   └── formatters.js      # Number/date formatting helpers
│   └── styles/
│       ├── tokens.css         # Design tokens (colors, spacing, radii)
│       ├── base.css           # Global resets, typography
│       ├── components.css     # Component-level styles
│       ├── layout.css         # Grid/flex layout utilities
│       └── legacy.css         # Back-compat utility classes
└── dist/                      # Production build output (generated)
```

---

## Setup

### Prerequisites
- **Node.js ≥ 18** (LTS recommended)
- **npm ≥ 9** (bundled with Node)

### Install Dependencies
```bash
cd D:\Axlero\frontend
npm install
```

### Development Server
```bash
npm run dev
```
- Starts Vite dev server (default: `http://localhost:5173`)
- Hot-module replacement enabled
- Open the printed URL in browser

### Production Build
```bash
npm run build
```
- Outputs optimized static assets to `dist/`
- Ready for deployment to any static host (Netlify, Vercel, S3, etc.)

### Preview Production Build
```bash
npm run preview
```
- Serves `dist/` locally for verification

---

## Current Frontend Functionality

### Implemented Pages (4 tabs)

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` (default) | Risk alert for shipment `MC-2048` (91% delay probability, 14-day predicted delay). Three prescriptive recommendations (Air Freight, Secondary Supplier, Delay Launch) with scores, costs, pros/cons, confidence breakdown. Execute Decision workflow with budget validation. |
| **Decisions** | `/decisions` | Write-back log table: date, action, predicted vs actual cost, outcome (Positive/Negative), status. Data from `localStorage` via `useDecisionHistory` hook. |
| **Analytics** | `/analytics` | ROI dashboard: decisions tracked, positive outcome rate, avg predicted vs actual cost. Bar chart comparing predicted vs actual cost per decision. Feedback loop explanation (4-step continuous learning). |
| **Settings** | `/settings` | Optimization constraint editor: maximum emergency budget ($), minimum protected inventory (units). Constraint list showing hard limits (budget, inventory) and business priority (delivery). Save shows toast confirmation. |

### Shared Features
- **Toast notifications** (success/error/info) via `useToast` hook
- **Error boundary** wraps entire app for graceful failure display
- **Responsive CSS** with design tokens, dark-friendly palette
- **System status indicator** in sidebar (shows "Model v1.0 • Ready")
- **Reset Demo** button clears `localStorage` and UI state

### Data Flow (Demo Mode)
All data is **static mock data** from `src/data/mockData.js`:
- `initialRecommendations` — 3 options with full prescriptive detail
- `initialHistory` — 3 completed decisions with predicted/actual costs
- `shipmentData` — Single at-risk shipment (MC-2048, microchips)
- `defaultConstraints` — Budget $20,000, inventory 250 units
- `modelInfo` — XGBoost + SciPy, v1.0, 87% accuracy

Decisions "executed" on Dashboard are appended to `localStorage` via `useDecisionHistory` and immediately visible on Decisions/Analytics tabs.

---

## Mock-Data Status

| Data | Source | Backend Replacement |
|------|--------|---------------------|
| Shipment risk alert | `mockData.js:shipmentData` | `GET /api/v1/shipments/{id}/risk` |
| Recommendations | `mockData.js:initialRecommendations` | `POST /api/v1/optimize` (or `GET /api/v1/recommendations`) |
| Decision history | `localStorage` (seeded from `initialHistory`) | `GET /api/v1/decisions` |
| ROI metrics | Computed from `localStorage` history | `GET /api/v1/roi` |
| Constraints | `mockData.js:defaultConstraints` + `localStorage` | `GET/PUT /api/v1/constraints` |
| Model info | `mockData.js:modelInfo` | `GET /api/v1/model/info` |

**No live API calls exist yet.** All network requests would fail; the UI is fully functional offline.

---

## Future Backend Integration

### Required Backend Endpoints (Not Yet Implemented)

| Frontend Action | Backend Endpoint | Method | Notes |
|-----------------|------------------|--------|-------|
| Load shipment risk | `/api/v1/shipments/{shipment_id}/risk` | GET | Returns delay probability, risk factors, financial exposure |
| Get recommendations | `/api/v1/optimize` | POST | Body: `{ shipment_id, constraints }` → returns ranked options |
| Execute decision | `/api/v1/decisions` | POST | Body: `{ recommendation_id, actor_id, override_reason? }` |
| List decisions | `/api/v1/decisions` | GET | Query: `cycle_id`, `status`, pagination |
| Get ROI analytics | `/api/v1/roi` | GET | Query: `date_range`, `group_by` |
| Get/set constraints | `/api/v1/constraints` | GET/PUT | Budget, inventory, delivery limits |
| Model metadata | `/api/v1/model/info` | GET | Version, accuracy, last retrained |

### Integration Steps
1. Replace `mockData.js` imports with API service layer (`src/services/api.js`)
2. Swap `useDecisionHistory` hook for server-backed data fetching (React Query / SWR recommended)
3. Add authentication context (JWT/OAuth) for `actor_id` on decisions
4. Connect Settings page constraints to `PUT /api/v1/constraints`
5. Wire Dashboard "Execute" button to `POST /api/v1/decisions` with optimistic UI update

---

## Current Project Status

| Area | Status |
|------|--------|
| **UI/UX** | ✅ Complete — 4 pages, responsive, accessible |
| **Component Library** | ✅ Complete — 8 reusable UI primitives |
| **State Management** | ✅ Complete — hooks + localStorage |
| **Styling System** | ✅ Complete — token-based CSS |
| **Mock Data** | ✅ Complete — realistic demo scenario |
| **Build/Dev Tooling** | ✅ Complete — Vite, ESLint-ready |
| **Backend API Integration** | ❌ **Not started** — all data is static |
| **Authentication** | ❌ Not implemented |
| **Real-time Updates** | ❌ Not implemented (WebSocket/SSE) |
| **Automated Tests** | ❌ Not configured (Vitest/Playwright pending) |
| **CI/CD** | ❌ Not configured |

---

## Notes for Contributors

- **No TypeScript yet** — codebase is plain JavaScript (`.jsx`). Migration planned.
- **No routing library** — page switching via `useState` in `main.jsx`. React Router can be added when page count grows.
- **No charting library** — Analytics bars are pure CSS. Recharts/D3 integration planned for richer visualizations.
- **Retool** — Separate operations interface (not in this repo). This React app targets analysts/executives.
- **Design tokens** — All colors, spacing, radii in `src/styles/tokens.css`. Modify there for theming.

---

## Related Repositories

- **Backend API** — `../backend/` (FastAPI, XGBoost/LightGBM/CatBoost ensemble, SciPy optimization)
- **ML Package** — `../SupplyPrescript_V2/supplyprescript/` (inference, preprocessing, artifacts)
- **Documentation** — `../README.md`, `../SupplyPrescript_README.md`
