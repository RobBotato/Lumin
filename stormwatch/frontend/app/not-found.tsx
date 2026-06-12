import { Radar } from "lucide-react";
import Link from "next/link";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="flex size-14 items-center justify-center rounded-2xl bg-accent/10">
        <Radar className="size-7 text-accent" />
      </div>
      <h1 className="mt-6 font-display text-2xl font-semibold">Page not found</h1>
      <p className="mt-2 text-sm text-muted">The page you&apos;re looking for doesn&apos;t exist.</p>
      <Link
        href="/"
        className="mt-8 inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 font-mono text-xs font-bold text-black shadow-[0_0_20px_-4px_var(--accent)] hover:bg-[#5ff0e4] transition-colors"
      >
        Go home
      </Link>
    </div>
  );
}
