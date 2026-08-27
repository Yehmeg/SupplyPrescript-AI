export function Spinner({ size = "md", className = "", "aria-label": ariaLabel = "Loading" }) {
  const sizeClasses = {
    sm: "spinner-sm",
    md: "",
    lg: "spinner-lg"
  }[size];

  const classNames = ["spinner", sizeClasses, className].filter(Boolean).join(" ");

  return (
    <span
      className={classNames}
      role="status"
      aria-label={ariaLabel}
      aria-hidden="true"
    >
      <span className="visually-hidden">{ariaLabel}</span>
    </span>
  );
}

export function SpinnerOverlay({ isVisible = true, message = "Processing...", className = "" }) {
  if (!isVisible) return null;

  return (
    <div className={`spinner-overlay ${className}`} role="status" aria-live="polite">
      <div className="spinner-overlay-content">
        <Spinner size="lg" aria-label={message} />
        <p className="spinner-message">{message}</p>
      </div>
    </div>
  );
}