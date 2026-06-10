import React from "react";

interface State {
  error: Error | null;
}

interface Props {
  children: React.ReactNode;
}

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="mx-auto max-w-xl rounded-xl border border-brand-red/40 bg-brand-red/10 p-6 text-brand-stone">
        <h2 className="mb-2 font-display text-xl text-brand-red">
          Something cracked the dice
        </h2>
        <p className="mb-3 text-sm text-brand-stone/80">
          The app hit an unexpected error and stopped. Reloading usually clears
          it; if it keeps happening, the trace is in the browser console.
        </p>
        <pre className="mb-4 max-h-32 overflow-auto rounded bg-ink-900 p-2 text-[11px] text-brand-stone/60">
          {this.state.error.message}
        </pre>
        <div className="flex gap-2">
          <button
            onClick={this.reset}
            className="rounded-lg border border-ink-500 bg-ink-700 px-3 py-1.5 font-heading text-xs text-brand-stone hover:border-brand-gold hover:text-brand-gold"
          >
            Try again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="rounded-lg bg-brand-red px-3 py-1.5 font-heading text-xs text-white hover:brightness-110"
          >
            Reload
          </button>
        </div>
      </div>
    );
  }
}
