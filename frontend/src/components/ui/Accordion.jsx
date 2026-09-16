import { useState, useId } from "react";

export function Accordion({ children, className = "", allowMultiple = false }) {
  return (
    <div className={`accordion ${className}`} data-allow-multiple={allowMultiple}>
      {children}
    </div>
  );
}

export function AccordionItem({ children, className = "", defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const triggerId = useId();
  const contentId = useId();

  const toggle = () => setIsOpen(!isOpen);

  return (
    <div className={`accordion-item ${className}`}>
      {React.Children.map(children, child => {
        if (!React.isValidElement(child)) return child;
        if (child.type === AccordionTrigger) {
          return React.cloneElement(child, {
            isOpen,
            onToggle: toggle,
            triggerId,
            contentId
          });
        }
        if (child.type === AccordionContent) {
          return React.cloneElement(child, {
            isOpen,
            contentId,
            triggerId
          });
        }
        return child;
      })}
    </div>
  );
}

export function AccordionTrigger({ children, isOpen, onToggle, triggerId, contentId, className = "", ...props }) {
  return (
    <button
      className={`accordion-trigger ${className}`}
      onClick={onToggle}
      aria-expanded={isOpen}
      aria-controls={contentId}
      id={triggerId}
      type="button"
      {...props}
    >
      <span className="accordion-trigger-content">{children}</span>
      <svg className="accordion-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>
  );
}

export function AccordionContent({ children, isOpen, contentId, triggerId, className = "", ...props }) {
  return (
    <div
      className={`accordion-content ${className}`}
      id={contentId}
      role="region"
      aria-labelledby={triggerId}
      hidden={!isOpen}
      {...props}
    >
      {isOpen && <div className="accordion-content-inner">{children}</div>}
    </div>
  );
}

Accordion.Trigger = AccordionTrigger;
Accordion.Content = AccordionContent;