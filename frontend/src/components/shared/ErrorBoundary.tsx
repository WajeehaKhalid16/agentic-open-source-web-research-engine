import React from 'react';
import { ErrorCard } from './ErrorCard';

interface State {
  hasError: boolean;
  message: string;
}

interface Props {
  label?: string;
  children?: React.ReactNode;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo): void {
    // Errors are captured in state via getDerivedStateFromError; info available for logging.
    console.error(`[ErrorBoundary:${this.props.label ?? 'component'}]`, error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorCard
          title={`Error in ${this.props.label ?? 'component'}`}
          message={this.state.message}
          onRetry={() => this.setState({ hasError: false, message: '' })}
          className="m-6"
        />
      );
    }
    return this.props.children ?? null;
  }
}
