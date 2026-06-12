"use client";
import { ArrowRight, Clock, DollarSign, Route } from "lucide-react";
import type { AlternativeRoute } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface Props { routes: AlternativeRoute[]; }
const RB: Record<string,"low"|"medium"|"high">={LOW:"low",MEDIUM:"medium",HIGH:"high"};

export function AlternativeRoutesCard({ routes }: Props) {
  if (!routes?.length) return null;
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2.5 mb-5"><Route className="size-4 text-accent" /><h3 className="font-display text-base font-semibold tracking-tight">Alternative Routes</h3><span className="ml-auto font-mono text-[11px] uppercase tracking-wider text-faint">{routes.length} options</span></div>
      <div className="space-y-3">
        {routes.map((r,i)=>(
          <div key={r.id} className="animate-fade-up rounded-xl border border-card-border bg-white/[0.02] p-4 transition-colors hover:border-accent/20" style={{animationDelay:`${0.1*i}s`}}>
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2"><span className="font-mono text-[11px] text-faint">Option {i+1}</span><Badge variant={RB[r.riskLevel]??"low"}>{r.riskLevel} Risk</Badge></div>
                <h4 className="mt-1 font-display text-sm font-semibold">{r.routeName}</h4>
                <div className="mt-1.5 flex items-center gap-2 font-mono text-[11px] text-muted"><span>{r.originPort}</span><ArrowRight className="size-3 text-faint" /><span>{r.destinationPort}</span></div>
                <p className="mt-2 text-xs leading-relaxed text-muted">{r.description}</p>
              </div>
            </div>
            <div className="mt-3 flex items-center gap-4 border-t border-card-border pt-3">
              <span className="flex items-center gap-1 font-mono text-[11px] text-faint"><Clock className="size-3" />+{r.additionalDays} days</span>
              <span className="flex items-center gap-1 font-mono text-[11px] text-faint"><DollarSign className="size-3" />${r.additionalCost.toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
