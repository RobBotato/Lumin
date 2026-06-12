"use client";

import Link from "next/link";
import { Radar } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";

export function SiteHeader() {
  const [calConnected, setCalConnected] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8080/api/auth/google/status")
      .then((r) => r.json())
      .then((d) => setCalConnected(d.connected))
      .catch(() => {});
  }, []);

  return (
    <header className="sticky top-0 z-40 border-b border-white/[0.06] bg-background/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-accent-deep shadow-[0_0_20px_-4px_var(--accent)] transition-shadow group-hover:shadow-[0_0_28px_-4px_var(--accent)]">
            <Radar className="size-4.5 text-accent-foreground" />
          </span>
          <span className="font-display text-[17px] font-semibold tracking-tight">
            Lumin
          </span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {["Platform", "Intelligence", "Network", "Docs"].map((item) => (
            <span key={item} className="cursor-default rounded-lg px-3 py-1.5 text-sm text-muted transition-colors hover:text-foreground">
              {item}
            </span>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          {calConnected ? (
            <span className="hidden sm:inline-flex items-center gap-2 rounded-full border border-green/30 bg-green/[0.08] px-3 py-1 font-mono text-[11px] text-green">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full rounded-full bg-green/60 [animation:radar-pulse_2s_ease-out_infinite]" />
                <span className="relative inline-flex size-2 rounded-full bg-green" />
              </span>
              Google Calendar · Live
            </span>
          ) : (
            <a
              href="http://localhost:8080/api/auth/google"
              className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-card-border bg-white/[0.03] px-3 py-1 font-mono text-[10px] text-muted hover:border-accent/30 hover:text-accent transition-colors"
            >
              Connect Calendar
            </a>
          )}
          <Button asChild size="sm">
            <Link href="/analyze">Analyze</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}
