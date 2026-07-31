import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button } from '@/design-system/primitives/Button';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallbackTitle?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      message: error.message || 'Something went wrong',
    };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('UI error boundary caught:', error, info.componentStack);
  }

  private reset = () => {
    this.setState({ hasError: false, message: '' });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div
          className="flex min-h-[320px] flex-col items-center justify-center gap-3 p-8 text-center"
          role="alert"
        >
          <h2 className="text-lg font-medium text-text-primary">
            {this.props.fallbackTitle ?? 'Unexpected error'}
          </h2>
          <p className="max-w-md text-sm text-text-secondary">{this.state.message}</p>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={this.reset}>
              Try again
            </Button>
            <Button variant="ghost" size="sm" onClick={() => window.location.assign('/')}>
              Go home
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
