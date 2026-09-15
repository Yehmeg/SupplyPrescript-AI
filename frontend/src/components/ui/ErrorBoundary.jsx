import React, { Component } from "react";

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '20px',
          background: '#1a1a2e',
          color: '#eaeaea',
          fontFamily: 'monospace',
          fontSize: '13px',
          lineHeight: '1.5',
          whiteSpace: 'pre-wrap',
          maxHeight: '90vh',
          overflow: 'auto'
        }}>
          <h2 style={{ color: '#f87171', margin: '0 0 12px' }}>Application Error</h2>
          <div style={{ marginBottom: '16px', color: '#fca5a5' }}>
            <strong>Message:</strong> {this.state.error?.message || String(this.state.error)}
          </div>
          <div style={{ color: '#93c5fd' }}>
            <strong>Component Stack:</strong>
            <pre style={{ margin: '8px 0 0', fontSize: '12px' }}>
              {this.state.errorInfo?.componentStack || 'No stack available'}
            </pre>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}