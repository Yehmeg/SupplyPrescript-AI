export function Card({
  children,
  variant = "default",
  padded = true,
  interactive = false,
  className = "",
  onClick,
  ...props
}) {
  const baseClasses = "card";
  const variantClasses = variant !== "default" ? `card-${variant}` : "";
  const paddedClasses = padded ? "card-padded" : "";
  const interactiveClasses = interactive ? "card-interactive" : "";

  const classNames = [
    baseClasses,
    variantClasses,
    paddedClasses,
    interactiveClasses,
    className
  ].filter(Boolean).join(" ");

  const handleKeyDown = (e) => {
    if (interactive && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      onClick?.(e);
    }
  };

  const Component = interactive ? "button" : "div";

  return (
    <Component
      className={classNames}
      onClick={interactive ? onClick : undefined}
      onKeyDown={interactive ? handleKeyDown : undefined}
      tabIndex={interactive ? 0 : undefined}
      role={interactive ? "button" : undefined}
      aria-pressed={interactive ? undefined : undefined}
      {...props}
    >
      {children}
    </Component>
  );
}