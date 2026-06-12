"use client";

import { AlertTriangle, ArrowLeft, RefreshCw } from "lucide-react";
import Link from "next/link";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-red-500/10">
        <AlertTriangle className="size-7 text-red-400" />
      </div>
      <h1 className="mt-6 font-display text-2xl font-semibold">Something went wrong</h1>
      <p className="mt-2 text-sm text-muted max-w-sm text-center">
        {error.message || "An unexpected error occurred. Please try again."}
      </p>
      <div className="mt-8 flex items-center gap-3">
        <button
          onClick={reset}
          className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 font-mono text-xs font-bold text-black shadow-[0_0_20px_-4px_var(--accent)] hover:bg-[#5ff0e4] transition-colors"
        >
          <RefreshCw className="size-3.5" />
          Try again
        </button>
        <Link
          href="/"
          className="inline-flex items-center gap-2 rounded-lg border border-card-border bg-white/[0.03] px-4 py-2 font-mono text-xs text-muted hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-3.5" />
          Go home
        </Link>
      </div>
    </div>
  );
}
