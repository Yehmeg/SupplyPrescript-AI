export function Button({
  children,
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  fullWidth = false,
  onClick,
  type = "button",
  className = "",
  "aria-label": ariaLabel,
  ...props
}) {
  const baseClasses = "btn";
  const variantClasses = `btn-${variant}`;
  const sizeClasses = size !== "md" ? `btn-${size}` : "";
  const widthClasses = fullWidth ? "btn-full" : "";
  const disabledClasses = disabled ? "disabled" : "";
  const loadingClasses = loading ? "loading" : "";

  const classNames = [
    baseClasses,
    variantClasses,
    sizeClasses,
    widthClasses,
    disabledClasses,
    loadingClasses,
    className
  ].filter(Boolean).join(" ");

  return (
    <button
      type={type}
      className={classNames}
      disabled={disabled || loading}
      onClick={onClick}
      aria-label={ariaLabel}
      aria-busy={loading}
      {...props}
    >
      {loading && <span className="spinner spinner-sm spinner-inline" aria-hidden="true" />}
      {children}
    </button>
  );
}