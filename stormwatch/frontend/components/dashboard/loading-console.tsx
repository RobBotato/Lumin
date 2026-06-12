"use client";

import { Check, Loader2, MoveRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { AGENT_PIPELINE } from "@/lib/mock-data";
import { cn } from "@/lib/utils";
import type { ShipmentInput } from "@/lib/types";

interface LoadingConsoleProps {
  shipment: ShipmentInput;
  completedSteps: number;
}

/** Full-width agent console shown while the risk pipeline "executes". */
export function LoadingConsole({ shipment, completedSteps }: LoadingConsoleProps) {
  return (
    <div className="animate-fade-in mx-auto max-w-xl pt-10">
      <div className="text-center">
        <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">
          Agent running
        </p>
        <h1 className="mt-3 flex items-center justify-center gap-3 font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {shipment.origin}
          <MoveRight className="size-5 text-accent" />
          {shipment.destination}
        </h1>
        <div className="mt-3 flex justify-center">
          <Badge variant="accent">{shipment.productType}</Badge>
        </div>
      </div>

      <div className="glass mt-10 rounded-2xl p-6 sm:p-7">
        <ul className="space-y-1">
          {AGENT_PIPELINE.map((step, i) => {
            const done = i < completedSteps;
            const active = i === completedSteps;
            return (
              <li
                key={step.id}
                className={cn(
                  "flex items-center gap-4 rounded-xl px-3 py-3 transition-all duration-300",
                  active && "bg-accent/[0.06]",
                  !done && !active && "opacity-35",
                )}
              >
                <span
                  className={cn(
                    "flex size-7 shrink-0 items-center justify-center rounded-full border transition-colors",
                    done && "border-accent/40 bg-accent/15 text-accent",
                    active && "border-accent/40 text-accent",
                    !done && !active && "border-card-border text-faint",
                  )}
                >
                  {done ? (
                    <Check className="animate-check-pop size-3.5" />
                  ) : active ? (
                    <Loader2 className="size-3.5 animate-spin" />
                  ) : (
                    <span className="size-1.5 rounded-full bg-current" />
                  )}
                </span>
                <span
                  className={cn(
                    "text-sm font-medium",
                    done ? "text-foreground" : active ? "text-foreground" : "text-muted",
                  )}
                >
                  {step.label}
                </span>
                {done && (
                  <span className="ml-auto font-mono text-[11px] text-faint">
                    {step.durationMs}ms
                  </span>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      <p className="mt-6 text-center font-mono text-[11px] text-faint">
        Cross-referencing 72h forecasts with cargo sensitivity profile…
      </p>
    </div>
  );
}
