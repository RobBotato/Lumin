import { Check, Workflow } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentEvent } from "@/lib/types";

interface AgentTimelineProps {
  events: AgentEvent[];
}

export function AgentTimeline({ events }: AgentTimelineProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex-row items-center justify-between space-y-0 pb-3">
        <div className="space-y-1.5">
          <CardTitle className="flex items-center gap-2">
            <Workflow className="size-4 text-accent" />
            Agent Activity
          </CardTitle>
          <CardDescription>Pipeline execution log</CardDescription>
        </div>
        <Badge variant="low">
          <span className="size-1.5 rounded-full bg-risk-low" />
          Complete
        </Badge>
      </CardHeader>

      <CardContent>
        <div className="flex items-start gap-0">
          {events.map((event, i) => (
            <div
              key={event.id}
              className="animate-fade-up flex-1 min-w-0"
              style={{ animationDelay: `${0.45 + i * 0.1}s` }}
            >
              <div className="flex items-center">
                <span className="relative z-10 flex size-[22px] shrink-0 items-center justify-center rounded-full border border-accent/40 bg-surface-raised text-accent shadow-[0_0_10px_-2px_var(--accent)]">
                  <Check className="size-3" />
                </span>
                {i < events.length - 1 && (
                  <div className="h-px flex-1 bg-accent/20" />
                )}
              </div>
              <div className="mt-2 pr-2">
                <p className="text-[12px] font-semibold leading-tight truncate">
                  {event.label}
                </p>
                <p className="mt-0.5 font-mono text-[10px] tabular-nums text-faint">
                  {event.timestamp}
                </p>
                <p className="mt-0.5 font-mono text-[10px] uppercase tracking-wider text-muted">
                  {event.durationMs}ms
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
