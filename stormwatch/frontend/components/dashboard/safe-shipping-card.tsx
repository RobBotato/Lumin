"use client";
import { Calendar, Check, ShieldAlert } from "lucide-react";
import type { SafeWindow } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props { windows: SafeWindow[]; }
export function SafeShippingCard({ windows }: Props) {
  if (!windows?.length) return null;
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2.5 mb-5">
        <Calendar className="size-4 text-accent" />
        <h3 className="font-display text-base font-semibold tracking-tight">Safe Shipping Windows</h3>
        <span className="ml-auto font-mono text-[11px] uppercase tracking-wider text-faint">7-Day Forecast</span>
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {windows.map(w=>(
          <div key={w.date} className={cn("relative flex flex-col items-center rounded-xl p-2.5 pt-3 transition-all",w.recommended?"bg-risk-low/10 border border-risk-low/25":w.riskLevel==="MEDIUM"?"bg-risk-medium/5 border border-risk-medium/20":"bg-risk-high/5 border border-risk-high/20")}>
            {w.recommended&&<div className="absolute -top-1.5 -right-1.5 flex size-4 items-center justify-center rounded-full bg-risk-low text-[8px] text-black"><Check className="size-2.5" /></div>}
            <span className="font-mono text-[9px] uppercase tracking-wider text-faint">{w.dayLabel.split(" ")[0]}</span>
            <span className="mt-0.5 font-display text-sm font-semibold">{w.dayLabel.split(" ")[1]} {w.dayLabel.split(" ")[2]}</span>
            <div className={cn("mt-2 w-full h-1 rounded-full",w.riskLevel==="HIGH"?"bg-risk-high/50":w.riskLevel==="MEDIUM"?"bg-risk-medium/50":"bg-risk-low/50")}>
              <div className={cn("h-full rounded-full transition-all duration-700",w.riskLevel==="HIGH"?"bg-risk-high w-[85%]":w.riskLevel==="MEDIUM"?"bg-risk-medium w-[50%]":"bg-risk-low w-[15%]")} />
            </div>
            <span className={cn("mt-1.5 font-mono text-[10px]",w.recommended?"text-risk-low":w.riskLevel==="MEDIUM"?"text-risk-medium":"text-risk-high")}>{w.riskLevel}</span>
          </div>
        ))}
      </div>
      {windows.some(w=>w.recommended)&&(
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-risk-low/5 border border-risk-low/15 px-3 py-2.5">
          <ShieldAlert className="size-3.5 text-risk-low shrink-0" />
          <p className="font-mono text-[11px] text-risk-low">Earliest safe departure: <span className="font-semibold">{windows.find(w=>w.recommended)?.dayLabel}</span></p>
        </div>
      )}
    </div>
  );
}
