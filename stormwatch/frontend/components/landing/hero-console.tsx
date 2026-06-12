import { CloudLightning, ShieldAlert, ThermometerSun } from "lucide-react";

import { Badge } from "@/components/ui/badge";

const LOG_LINES = [
  { text: "shipment.received  VAX-20847  PHX → DAL", tone: "text-muted" },
  { text: "forecast.fetch     14 waypoints · 72h window", tone: "text-muted" },
  { text: "threat.detected    extreme_heat  p=0.88", tone: "text-risk-high" },
  { text: "threat.detected    humidity      p=0.64", tone: "text-risk-medium" },
  { text: "sensitivity.match  biologics · 2–8°C cold chain", tone: "text-muted" },
  { text: "plan.generated     3 mitigations ranked", tone: "text-accent" },
] as const;

/**
 * Decorative agent console for the hero — log lines stream in on page load
 * via staggered CSS animations.
 */
export function HeroConsole() {
  return (
    <div className="glass relative overflow-hidden rounded-2xl p-1.5">
      {/* glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 right-0 size-64 rounded-full bg-accent/10 blur-3xl [animation:glow-breathe_5s_ease-in-out_infinite]"
      />

      {/* title bar */}
      <div className="flex items-center justify-between rounded-t-xl px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="size-2.5 rounded-full bg-white/10" />
          <span className="size-2.5 rounded-full bg-white/10" />
          <span className="size-2.5 rounded-full bg-white/10" />
        </div>
        <span className="font-mono text-[11px] uppercase tracking-widest text-faint">
          risk-agent · live
        </span>
        <span className="relative flex size-2">
          <span className="absolute inline-flex size-full rounded-full bg-accent opacity-60 [animation:radar-pulse_2s_ease-out_infinite]" />
          <span className="relative inline-flex size-2 rounded-full bg-accent" />
        </span>
      </div>

      {/* log body */}
      <div className="rounded-xl bg-black/40 p-5 font-mono text-[12.5px] leading-7">
        {LOG_LINES.map((line, i) => (
          <p
            key={line.text}
            className={`${line.tone} animate-fade-up whitespace-pre`}
            style={{ animationDelay: `${0.5 + i * 0.35}s` }}
          >
            <span className="mr-3 text-faint">{String(i + 1).padStart(2, "0")}</span>
            {line.text}
          </p>
        ))}
        <p
          className="animate-fade-up mt-1 text-faint"
          style={{ animationDelay: `${0.5 + LOG_LINES.length * 0.35}s` }}
        >
          <span className="mr-3 text-faint">—</span>
          analysis complete in 2.24s
          <span className="animate-blink ml-1 inline-block h-3.5 w-1.5 translate-y-0.5 bg-accent/70" />
        </p>
      </div>

      {/* result strip */}
      <div
        className="animate-fade-up flex flex-wrap items-center gap-2.5 px-4 py-3.5"
        style={{ animationDelay: "2.9s" }}
      >
        <Badge variant="high">
          <ShieldAlert className="size-3" />
          High Risk · 84
        </Badge>
        <Badge variant="medium">
          <ThermometerSun className="size-3" />
          Extreme Heat
        </Badge>
        <Badge>
          <CloudLightning className="size-3" />
          Storms 42%
        </Badge>
        <span className="ml-auto font-mono text-[11px] text-faint">conf 94%</span>
      </div>
    </div>
  );
}
