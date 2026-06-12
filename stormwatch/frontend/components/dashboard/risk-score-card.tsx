"use client";

import * as React from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { RISK_META } from "@/lib/presentation";
import type { WeatherRiskAnalysis } from "@/lib/types";

const GAUGE_RADIUS = 84;
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * GAUGE_RADIUS;
/** The gauge is a 270° arc (three quarters of the circle). */
const ARC_FRACTION = 0.75;

/** Animate a number from 0 to `target` with an ease-out curve. */
function useCountUp(target: number, durationMs = 1400): number {
  const [value, setValue] = React.useState(0);

  React.useEffect(() => {
    let frame: number;
    const start = performance.now();

    const tick = (now: number) => {
      const progress = Math.min((now - start) / durationMs, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(Math.round(target * eased));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}

interface RiskScoreCardProps {
  analysis: WeatherRiskAnalysis;
}

export function RiskScoreCard({ analysis }: RiskScoreCardProps) {
  const { riskLevel, riskScore, confidence, summary } = analysis;
  const meta = RISK_META[riskLevel];

  const animatedScore = useCountUp(riskScore);
  const animatedConfidence = useCountUp(confidence, 1600);

  const [mounted, setMounted] = React.useState(false);
  React.useEffect(() => {
    const frame = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  const arcLength = GAUGE_CIRCUMFERENCE * ARC_FRACTION;
  const filled = mounted ? arcLength * (riskScore / 100) : 0;

  return (
    <Card className="relative h-full overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-20 left-1/2 size-72 -translate-x-1/2 rounded-full blur-3xl"
        style={{ background: meta.color, opacity: 0.09 }}
      />

      <CardContent className="flex h-full flex-col items-center p-7">
        <div className="flex w-full items-center justify-between">
          <h3 className="font-display text-base font-semibold tracking-tight">
            Risk Score
          </h3>
          <Badge variant={riskLevel === "LOW" ? "low" : riskLevel === "MEDIUM" ? "medium" : "high"}>
            {riskLevel}
          </Badge>
        </div>

        {/* Gauge */}
        <div className="relative mt-6">
          <svg width="220" height="200" viewBox="0 0 220 200">
            <g transform="rotate(135 110 110)">
              <circle
                cx="110"
                cy="110"
                r={GAUGE_RADIUS}
                fill="none"
                stroke="rgba(255,255,255,0.07)"
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${arcLength} ${GAUGE_CIRCUMFERENCE}`}
              />
              <circle
                cx="110"
                cy="110"
                r={GAUGE_RADIUS}
                fill="none"
                stroke={meta.color}
                strokeWidth="12"
                strokeLinecap="round"
                strokeDasharray={`${filled} ${GAUGE_CIRCUMFERENCE}`}
                style={{
                  transition: "stroke-dasharray 1.4s cubic-bezier(0.22, 1, 0.36, 1)",
                  filter: `drop-shadow(0 0 10px ${meta.color})`,
                }}
              />
            </g>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
            <span
              className="font-display text-6xl font-semibold tracking-tight"
              style={{ color: meta.color }}
            >
              {animatedScore}
            </span>
            <span className="mt-1 font-mono text-[11px] uppercase tracking-[0.16em] text-faint">
              / 100
            </span>
          </div>
        </div>

        <p
          className="font-display text-2xl font-semibold tracking-tight"
          style={{ color: meta.color }}
        >
          {meta.label}
        </p>
        <p className="mt-1 text-center text-sm text-muted">{meta.description}</p>

        {/* Confidence */}
        <div className="mt-6 w-full">
          <div className="flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.14em]">
            <span className="text-faint">Model confidence</span>
            <span className="text-foreground">{animatedConfidence}%</span>
          </div>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
            <div
              className="animate-bar-grow h-full rounded-full bg-gradient-to-r from-accent-deep to-accent"
              style={{ width: `${confidence}%`, animationDelay: "0.3s" }}
            />
          </div>
        </div>

        <p className="mt-6 border-t border-white/[0.06] pt-5 text-sm leading-relaxed text-muted">
          {summary}
        </p>
      </CardContent>
    </Card>
  );
}
