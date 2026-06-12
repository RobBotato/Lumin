"use client";

import { FileText, ShieldAlert, TrendingUp } from "lucide-react";
import type { ExecutiveSummary } from "@/lib/types";

interface Props {
  summary: ExecutiveSummary;
}

export function ExecutiveSummaryCard({ summary }: Props) {
  if (!summary) return null;

  return (
    <div className="glass rounded-2xl p-6 border-accent/20 bg-accent/[0.02]">
      <div className="flex items-center gap-2.5 mb-4">
        <FileText className="size-4 text-accent" />
        <h3 className="font-display text-base font-semibold tracking-tight">Executive Summary</h3>
        <span className="ml-auto font-mono text-[10px] uppercase tracking-wider text-accent">AI Generated</span>
      </div>

      {/* Main Risks */}
      <div className="mb-4">
        <div className="flex items-center gap-1.5 mb-2">
          <ShieldAlert className="size-3 text-risk-high" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-risk-high">Main Risks</span>
        </div>
        <ul className="space-y-1.5">
          {summary.mainRisks?.map((risk, i) => (
            <li key={i} className="flex items-start gap-2 font-mono text-[11px] text-muted leading-relaxed">
              <span className="mt-0.5 size-1.5 shrink-0 rounded-full bg-risk-high" />
              {risk}
            </li>
          ))}
        </ul>
      </div>

      {/* Business Impact */}
      <div className="mb-4 p-3 rounded-xl border border-risk-high/20 bg-risk-high/[0.03]">
        <div className="flex items-center gap-1.5 mb-1">
          <TrendingUp className="size-3 text-risk-high" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-risk-high">Business Impact</span>
        </div>
        <p className="font-mono text-[11px] text-muted leading-relaxed">{summary.businessImpact}</p>
      </div>

      {/* Top Recommendations */}
      <div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-accent">Top Recommendations</span>
        <ul className="mt-1.5 space-y-1">
          {summary.topRecommendations?.map((rec, i) => (
            <li key={i} className="flex items-start gap-2 font-mono text-[11px] text-muted leading-relaxed">
              <span className="mt-0.5 font-bold text-accent">{i + 1}.</span>
              {rec}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
