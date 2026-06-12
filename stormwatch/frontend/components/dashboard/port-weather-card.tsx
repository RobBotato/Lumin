"use client";
import { Anchor, Cloud, Eye, Gauge, Wind } from "lucide-react";
import type { PortWeather } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface Props { portWeather: PortWeather; }
export function PortWeatherCard({ portWeather }: Props) {
  if (!portWeather) return null;
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2.5 mb-5"><Anchor className="size-4 text-accent" /><h3 className="font-display text-base font-semibold tracking-tight">Port Conditions</h3></div>
      <div className="grid gap-4 sm:grid-cols-2">
        {(["origin","destination"] as const).map(key=>{
          const p=portWeather[key];
          return (
            <div key={key} className={cn("rounded-xl border p-4",p.status==="restricted"?"border-risk-high/30 bg-risk-high/[0.03]":"border-card-border bg-white/[0.02]")}>
              <div className="flex items-center justify-between mb-3"><span className="font-mono text-[10px] uppercase tracking-wider text-faint">{key==="origin"?"Origin Port":"Destination Port"}</span><Badge variant={p.status==="restricted"?"high":"low"}>{p.status}</Badge></div>
              <p className="font-display text-sm font-semibold">{p.portName}</p>
              <div className="mt-3 grid grid-cols-2 gap-2">
                <div className="flex items-center gap-1.5 text-xs text-muted"><Cloud className="size-3 text-faint" />{p.conditions}</div>
                <div className="flex items-center gap-1.5 text-xs text-muted"><Gauge className="size-3 text-faint" />{p.temperature}</div>
                <div className="flex items-center gap-1.5 text-xs text-muted"><Wind className="size-3 text-faint" />{p.windSpeed}</div>
                <div className="flex items-center gap-1.5 text-xs text-muted"><Eye className="size-3 text-faint" />{p.visibility}</div>
              </div>
              <div className="mt-3 flex items-center gap-1.5 pt-2 border-t border-card-border"><span className="font-mono text-[9px] uppercase text-faint">Storm:</span><span className={cn("font-mono text-[10px]",p.status==="restricted"?"text-risk-high":"text-risk-low")}>{p.stormProximity}</span></div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
