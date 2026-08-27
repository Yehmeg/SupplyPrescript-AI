export function formatCurrency(value, options = {}) {
  const { compact = false, showSign = false } = options;
  if (value === null || value === undefined) return "—";
  
  const absValue = Math.abs(value);
  const sign = value < 0 ? "-" : showSign && value > 0 ? "+" : "";
  
  if (compact && absValue >= 1000000) {
    return `${sign}$${(absValue / 1000000).toFixed(1)}M`;
  }
  if (compact && absValue >= 1000) {
    return `${sign}$${(absValue / 1000).toFixed(1)}K`;
  }
  
  return `${sign}$${absValue.toLocaleString()}`;
}

export function formatNumber(value, options = {}) {
  const { decimals = 0, compact = false } = options;
  if (value === null || value === undefined) return "—";
  
  if (compact && Math.abs(value) >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (compact && Math.abs(value) >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  
  return value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

export function formatPercent(value, options = {}) {
  const { decimals = 0, showSign = false } = options;
  if (value === null || value === undefined) return "—";
  
  const percent = value * 100;
  const sign = percent < 0 ? "-" : showSign && percent > 0 ? "+" : "";
  return `${sign}${Math.abs(percent).toFixed(decimals)}%`;
}

export function formatDate(date, options = {}) {
  const { format = "short", locale = "en-US" } = options;
  if (!date) return "—";
  
  const d = new Date(date);
  if (isNaN(d.getTime())) return "—";
  
  const configs = {
    short: { day: "2-digit", month: "short", year: "numeric" },
    long: { weekday: "short", day: "2-digit", month: "short", year: "numeric" },
    time: { hour: "2-digit", minute: "2-digit" },
    datetime: { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }
  };
  
  return d.toLocaleDateString(locale, configs[format] || configs.short);
}

export function formatRelativeTime(date) {
  if (!date) return "—";
  const d = new Date(date);
  if (isNaN(d.getTime())) return "—";
  
  const now = new Date();
  const diffMs = now - d;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(d, { format: "short" });
}

export function formatRiskLevel(risk) {
  const levels = {
    low: { label: "Low", class: "badge-success" },
    medium: { label: "Medium", class: "badge-warning" },
    high: { label: "High", class: "badge-danger" }
  };
  const key = risk.toLowerCase();
  return levels[key] || { label: risk, class: "badge-neutral" };
}

export function formatOutcome(outcome) {
  const outcomes = {
    positive: { label: "Positive", class: "badge-success" },
    negative: { label: "Negative", class: "badge-danger" },
    pending: { label: "Pending", class: "badge-warning" }
  };
  const key = outcome.toLowerCase();
  return outcomes[key] || { label: outcome, class: "badge-neutral" };
}

export function formatStatus(status) {
  const statuses = {
    completed: { label: "Completed", class: "badge-success" },
    executed: { label: "Executed", class: "badge-primary" },
    pending: { label: "Pending", class: "badge-warning" },
    failed: { label: "Failed", class: "badge-danger" }
  };
  const key = status.toLowerCase();
  return statuses[key] || { label: status, class: "badge-neutral" };
}

export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + "…";
}

export function calculateAccuracy(predicted, actual) {
  if (!predicted || predicted === 0) return null;
  const error = Math.abs(predicted - actual) / predicted;
  return Math.max(0, 1 - error);
}

export function calculateROI(predicted, actual) {
  if (!predicted || predicted === 0) return null;
  return ((actual - predicted) / predicted) * 100;
}