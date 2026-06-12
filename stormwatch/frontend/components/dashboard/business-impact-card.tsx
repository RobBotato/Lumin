"use client";

import { Briefcase, DollarSign, AlertTriangle, TrendingUp, Clock } from "lucide-react";
import type { BusinessImpact } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props {
  impact: BusinessImpact;
}

export function BusinessImpactCard({ impact }: Props) {
  if (!impact) return null;

  const exposurePercent = Math.round((impact.estimatedExposure / impact.shipmentValue) * 100);

  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2.5 mb-5">
        <Briefcase className="size-4 text-accent" />
        <h3 className="font-display text-base font-semibold tracking-tight">Business Impact</h3>
      </div>

      {/* Shipment Value */}
      <div className="mb-4 p-4 rounded-xl border border-card-border bg-white/[0.02]">
        <div className="flex items-center gap-2 mb-1">
          <DollarSign className="size-3.5 text-foreground" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-faint">Shipment Value</span>
        </div>
        <p className="font-display text-2xl font-semibold">${impact.shipmentValue.toLocaleString()}</p>
      </div>

      {/* Estimated Exposure */}
      <div className="mb-4 p-4 rounded-xl border border-risk-high/30 bg-risk-high/[0.03]">
        <div className="flex items-center gap-2 mb-1">
          <AlertTriangle className="size-3.5 text-risk-high" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-risk-high">Estimated Exposure</span>
        </div>
        <p className="font-display text-2xl font-semibold text-risk-high">${impact.estimatedExposure.toLocaleString()}</p>
        <div className="mt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="font-mono text-[9px] text-faint">{exposurePercent}% of shipment value</span>
            <span className="font-mono text-[9px] text-faint">Confidence: {impact.confidenceLevel}</span>
          </div>
          <div className="h-1.5 w-full rounded-full bg-white/[0.04]">
            <div
              className="h-full rounded-full bg-risk-high/60 transition-all duration-700"
              style={{ width: `${Math.min(exposurePercent, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Operational Impact */}
      <div className="mb-4 p-3 rounded-xl border border-accent/15 bg-accent/[0.02]">
        <div className="flex items-center gap-2 mb-1">
          <TrendingUp className="size-3.5 text-accent" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-accent">Operational Impact</span>
        </div>
        <p className="font-mono text-[11px] text-muted leading-relaxed">{impact.operationalImpact}</p>
      </div>

      {/* Delay Cost Per Day */}
      <div className="flex items-center justify-between p-3 rounded-xl border border-card-border bg-white/[0.01]">
        <div className="flex items-center gap-2">
          <Clock className="size-3.5 text-faint" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-faint">Delay Cost / Day</span>
        </div>
        <span className="font-mono text-sm font-bold">${impact.delayCostPerDay.toLocaleString()}</span>
      </div>
    </div>
  );
}
