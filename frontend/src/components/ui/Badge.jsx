export function Badge({
  children,
  variant = "neutral",
  dot = false,
  className = "",
  ...props
}) {
  const baseClasses = "badge";
  const variantClasses = `badge-${variant}`;
  const dotClasses = dot ? "badge-dot" : "";

  const classNames = [
    baseClasses,
    variantClasses,
    dotClasses,
    className
  ].filter(Boolean).join(" ");

  return (
    <span className={classNames} {...props}>
      {children}
    </span>
  );
}