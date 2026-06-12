"use client";
import { DollarSign, TrendingDown } from "lucide-react";
import type { FinancialBreakdown } from "@/lib/types";

interface Props { breakdown: FinancialBreakdown; }
export function FinancialBreakdownCard({ breakdown }: Props) {
  if (!breakdown) return null;
  const items = [
    {label:"Cargo Value",value:breakdown.cargoValue,color:"text-foreground"},
    {label:"Est. Delay Cost",value:breakdown.estimatedDelayCost,color:"text-risk-medium"},
    {label:"Demurrage Fees",value:breakdown.demurrageFees,color:"text-risk-medium"},
    {label:"Insurance Exposure",value:breakdown.insuranceExposure,color:"text-risk-medium"},
    {label:"Spoilage Risk",value:breakdown.spoilageRisk,color:breakdown.spoilageRisk>0?"text-risk-high":"text-faint"},
    {label:"Rerouting Cost",value:breakdown.reroutingCost,color:"text-accent"},
  ];
  const max=Math.max(...items.map(i=>i.value),1);
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2.5 mb-5"><DollarSign className="size-4 text-accent" /><h3 className="font-display text-base font-semibold tracking-tight">Financial Impact</h3><span className="ml-auto font-mono text-[11px] uppercase tracking-wider text-faint">{breakdown.currency}</span></div>
      <div className="mb-5 rounded-xl bg-risk-high/5 border border-risk-high/20 p-4">
        <p className="font-mono text-[10px] uppercase tracking-wider text-risk-high">Total Value at Risk</p>
        <p className="mt-1 font-display text-2xl font-semibold text-risk-high">${breakdown.totalAtRisk.toLocaleString()}</p>
      </div>
      <div className="space-y-3">
        {items.map(item=>(
          <div key={item.label}>
            <div className="flex items-center justify-between mb-1"><span className="font-mono text-[11px] text-muted">{item.label}</span><span className={`font-mono text-[11px] font-medium ${item.color}`}>${item.value.toLocaleString()}</span></div>
            <div className="h-1.5 w-full rounded-full bg-white/[0.04]"><div className={`h-full rounded-full transition-all duration-700 ${item.color.includes("risk-high")?"bg-risk-high/60":item.color.includes("risk-medium")?"bg-risk-medium/60":item.color.includes("accent")?"bg-accent/60":"bg-white/20"}`} style={{width:`${(item.value/max)*100}%`}} /></div>
          </div>
        ))}
      </div>
      {breakdown.estimatedSavingsIfRerouted>0&&(
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-risk-low/5 border border-risk-low/15 px-3 py-2.5">
          <TrendingDown className="size-3.5 text-risk-low shrink-0" />
          <p className="font-mono text-[11px] text-risk-low">Save up to <span className="font-semibold">${breakdown.estimatedSavingsIfRerouted.toLocaleString()}</span> by rerouting now</p>
        </div>
      )}
    </div>
  );
}
