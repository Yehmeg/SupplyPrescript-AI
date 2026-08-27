import { useEffect, useRef } from "react";
import { Button } from "./Button";

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  showClose = true,
  footer,
  className = "",
  "aria-describedby": ariaDescribedby
}) {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement;
      document.body.style.overflow = "hidden";
      modalRef.current?.focus();
      const handleKeyDown = (e) => {
        if (e.key === "Escape") onClose();
        if (e.key === "Tab") trapFocus(e);
      };
      document.addEventListener("keydown", handleKeyDown);
      return () => {
        document.body.style.overflow = "";
        document.removeEventListener("keydown", handleKeyDown);
        previousActiveElement.current?.focus();
      };
    }
  }, [isOpen, onClose]);

  const trapFocus = (e) => {
    if (!modalRef.current) return;
    const focusableElements = modalRef.current.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault();
      lastElement.focus();
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault();
      firstElement.focus();
    }
  };

  if (!isOpen) return null;

  const sizeClasses = {
    sm: "modal-sm",
    md: "modal-md",
    lg: "modal-lg"
  }[size];

  return (
    <div className="modal-backdrop" onClick={onClose} aria-hidden="true" />
    <div
      ref={modalRef}
      className={`modal ${sizeClasses} ${className}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
      aria-describedby={ariaDescribedby}
      tabIndex="-1"
      onClick={(e) => e.stopPropagation()}
    >
      {(title || showClose) && (
        <div className="modal-header">
          {title && <h2 id="modal-title" className="modal-title">{title}</h2>}
          {showClose && (
            <Button
              variant="ghost"
              size="sm"
              className="modal-close"
              onClick={onClose}
              aria-label="Close modal"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </Button>
          )}
        </div>
      )}
      <div className="modal-body" id={ariaDescribedby}>
        {children}
      </div>
      {footer && (
        <div className="modal-footer">
          {footer}
        </div>
      )}
    </div>
  );
}