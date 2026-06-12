"use client";
import { Shield, Scale, Zap } from "lucide-react";
import type { RiskTolerance } from "@/lib/types";
import { cn } from "@/lib/utils";

interface Props { value: RiskTolerance; onChange: (v: RiskTolerance) => void; }
const OPTIONS: { value: RiskTolerance; icon: typeof Shield; label: string; desc: string }[] = [
  { value:"Conservative", icon:Shield, label:"Conservative", desc:"Err on the side of caution. Prefer delay over risk." },
  { value:"Balanced", icon:Scale, label:"Balanced", desc:"Weigh cost against risk. Default recommendation strategy." },
  { value:"Aggressive", icon:Zap, label:"Aggressive", desc:"Minimize delays. Accept moderate risk." },
];

export function RiskToleranceSlider({ value, onChange }: Props) {
  return (
    <div className="space-y-2.5">
      <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-faint">Risk Tolerance — Controls how cautious recommendations should be</span>
      <div className="grid grid-cols-3 gap-1.5 rounded-xl border border-card-border bg-white/[0.02] p-1">
        {OPTIONS.map(opt=>{const active=value===opt.value;const Icon=opt.icon;return(
          <button key={opt.value} type="button" onClick={()=>onChange(opt.value)} className={cn("flex items-center justify-center gap-2 rounded-lg py-2 px-2 font-mono text-[11px] font-medium transition-all duration-200",active?"bg-accent/[0.12] text-accent border border-accent/30 shadow-[0_0_12px_-2px_var(--accent)]":"text-muted hover:text-foreground hover:bg-white/[0.04]")}>
            <Icon className={cn("size-3.5",active?"text-accent":"text-faint")} />{opt.label}
          </button>
        )})}
      </div>
      <p className="font-mono text-[10px] text-faint leading-relaxed">{OPTIONS.find(o=>o.value===value)?.desc}</p>
    </div>
  );
}
