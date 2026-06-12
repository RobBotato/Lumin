"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { ArrowRight, Box, DollarSign, MoveRight, RotateCcw, Scale, Truck, AlertTriangle, AlertCircle } from "lucide-react";

import { AgentTimeline } from "@/components/dashboard/agent-timeline";
import { AlternativeRoutesCard } from "@/components/dashboard/alternative-routes-card";
import { BusinessImpactCard } from "@/components/dashboard/business-impact-card";
import { ExecutiveSummaryCard } from "@/components/dashboard/executive-summary-card";
import { FinancialBreakdownCard } from "@/components/dashboard/financial-breakdown-card";
import { LoadingConsole } from "@/components/dashboard/loading-console";
import { PortWeatherCard } from "@/components/dashboard/port-weather-card";
import { RecommendationsCard } from "@/components/dashboard/recommendations-card";
import { RescheduleBanner } from "@/components/dashboard/reschedule-banner";
import { RiskScoreCard } from "@/components/dashboard/risk-score-card";
import { SafeShippingCard } from "@/components/dashboard/safe-shipping-card";
import { ThreatsCard } from "@/components/dashboard/threats-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AGENT_PIPELINE } from "@/lib/mock-data";
import { getWeatherRiskAnalysis, StormwatchError } from "@/lib/services/weather-risk";
import { type ShipmentInput, type WeatherRiskAnalysis } from "@/lib/types";

const STEP_INTERVAL_MS = 480;

function parseShipment(params: URLSearchParams): ShipmentInput {
  return {
    productType: params.get("product") || "Consumer Goods",
    origin: params.get("origin") || "Phoenix, AZ",
    destination: params.get("destination") || "Dallas, TX",
    shippingDate: params.get("date") || new Date().toISOString().slice(0, 10),
    quantity: params.get("quantity") ? parseInt(params.get("quantity")!) : undefined,
    estimatedWeight: params.get("weight") ? parseFloat(params.get("weight")!) : undefined,
    weightUnit: (params.get("weightUnit") as "kg" | "lbs") || undefined,
    shipmentValue: params.get("value") ? parseInt(params.get("value")!) : undefined,
    packagingType: params.get("packaging") as ShipmentInput["packagingType"] || undefined,
    transportMethod: params.get("transport") as ShipmentInput["transportMethod"] || undefined,
    deliveryPriority: params.get("priority") as ShipmentInput["deliveryPriority"] || undefined,
    riskTolerance: params.get("tolerance") as ShipmentInput["riskTolerance"] || undefined,
    clientPhone: params.get("clientPhone") || undefined,
    clientName: params.get("clientName") || undefined,
    clientEmail: params.get("clientEmail") || undefined,
  };
}

function formatDate(isoDate: string): string {
  const date = new Date(`${isoDate}T12:00:00`);
  if (Number.isNaN(date.getTime())) return isoDate;
  return date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}

export function AnalysisView() {
  const searchParams = useSearchParams();
  const shipment = React.useMemo(() => parseShipment(searchParams), [searchParams]);

  const [analysis, setAnalysis] = React.useState<WeatherRiskAnalysis | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [completedSteps, setCompletedSteps] = React.useState(0);

  React.useEffect(() => {
    let cancelled = false;
    getWeatherRiskAnalysis(shipment)
      .then((result) => { if (!cancelled) setAnalysis(result); })
      .catch((err) => { if (!cancelled) setError(err instanceof StormwatchError ? err.message : "An unexpected error occurred. Please try again."); });
    const timers = AGENT_PIPELINE.map((_, i) => setTimeout(() => { if (!cancelled) setCompletedSteps(i + 1); }, (i + 1) * STEP_INTERVAL_MS));
    return () => { cancelled = true; timers.forEach(clearTimeout); };
  }, [shipment]);

  const ready = analysis !== null && completedSteps >= AGENT_PIPELINE.length;

  if (error) {
    return (
      <div className="animate-fade-up mx-auto max-w-lg pt-20 text-center">
        <div className="glass rounded-2xl p-8">
          <AlertCircle className="mx-auto size-10 text-risk-high" />
          <h2 className="mt-4 font-display text-xl font-semibold">Agent Unavailable</h2>
          <p className="mt-2 text-sm text-muted leading-relaxed">{error}</p>
          <Button asChild variant="outline" size="sm" className="mt-6">
            <Link href="/analyze"><RotateCcw />Try again</Link>
          </Button>
        </div>
      </div>
    );
  }

  if (!ready) return <LoadingConsole shipment={shipment} completedSteps={completedSteps} />;

  return (
    <div>
      {/* Shipment summary bar */}
      <div className="animate-fade-up flex flex-wrap items-center gap-x-6 gap-y-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">Risk analysis complete</p>
          <h1 className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            {analysis.shipment.origin}<MoveRight className="size-7 text-accent" />{analysis.shipment.destination}
          </h1>
          {(analysis.shipment.quantity || analysis.shipment.estimatedWeight || analysis.shipment.shipmentValue) && (
            <div className="mt-2 flex flex-wrap items-center gap-3 font-mono text-xs text-faint">
              {analysis.shipment.quantity && <span>×{analysis.shipment.quantity?.toLocaleString()} units</span>}
              {analysis.shipment.estimatedWeight && <span className="flex items-center gap-1"><Scale className="size-3" />{analysis.shipment.estimatedWeight?.toLocaleString()} {analysis.shipment.weightUnit || "kg"}</span>}
              {analysis.shipment.shipmentValue && <span className="flex items-center gap-1"><DollarSign className="size-3" />${analysis.shipment.shipmentValue?.toLocaleString()}</span>}
            </div>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2 sm:ml-auto">
          <Badge variant="accent">{analysis.shipment.productType}</Badge>
          <Badge>{formatDate(analysis.shipment.shippingDate)}</Badge>
          {analysis.shipment.packagingType && <Badge variant="low"><Box className="size-3" />{analysis.shipment.packagingType}</Badge>}
          {analysis.shipment.transportMethod && <Badge variant="medium"><Truck className="size-3" />{analysis.shipment.transportMethod}</Badge>}
          {analysis.shipment.deliveryPriority && <Badge variant={analysis.shipment.deliveryPriority === "Critical" ? "high" : "default"}><AlertTriangle className="size-3" />{analysis.shipment.deliveryPriority}</Badge>}
          <Button asChild variant="outline" size="sm" className="ml-1"><Link href="/analyze"><RotateCcw />New analysis</Link></Button>
        </div>
      </div>

      {/* Auto-reschedule banner */}
      {analysis.rescheduledTo && (
        <div className="mt-6">
          <RescheduleBanner reschedule={analysis.rescheduledTo} shipment={analysis.shipment} />
        </div>
      )}

      {/* Results grid */}
      <div className="mt-8 space-y-5">
        {/* Row 0: Executive Summary — full width */}
        {analysis.executiveSummary && (
          <div className="animate-fade-up" style={{ animationDelay: "0.05s" }}>
            <ExecutiveSummaryCard summary={analysis.executiveSummary} />
          </div>
        )}

        {/* Row 1: Risk score + Business Impact */}
        <div className="grid gap-5 lg:grid-cols-12">
          <div className="animate-fade-up lg:col-span-4" style={{ animationDelay: "0.1s" }}>
            <RiskScoreCard analysis={analysis} />
          </div>
          <div className="animate-fade-up lg:col-span-8" style={{ animationDelay: "0.15s" }}>
            {analysis.businessImpact ? (
              <BusinessImpactCard impact={analysis.businessImpact} />
            ) : (
              <ThreatsCard threats={analysis.threats} />
            )}
          </div>
        </div>

        {/* Row 2: Threats */}
        <div className="animate-fade-up" style={{ animationDelay: "0.2s" }}>
          <ThreatsCard threats={analysis.threats} />
        </div>

        {analysis.safeShippingWindows?.length ? (
          <div className="animate-fade-up" style={{ animationDelay: "0.3s" }}><SafeShippingCard windows={analysis.safeShippingWindows} /></div>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-12">
          <div className="animate-fade-up lg:col-span-6" style={{ animationDelay: "0.4s" }}>
            {analysis.alternativeRoutes?.length ? <AlternativeRoutesCard routes={analysis.alternativeRoutes} /> : <RecommendationsCard recommendations={analysis.recommendations} />}
          </div>
          <div className="animate-fade-up lg:col-span-6" style={{ animationDelay: "0.5s" }}>
            {analysis.financialBreakdown ? <FinancialBreakdownCard breakdown={analysis.financialBreakdown} /> : <AgentTimeline events={analysis.agentEvents} />}
          </div>
        </div>

        <div className="grid gap-5 lg:grid-cols-12">
          <div className="animate-fade-up lg:col-span-6" style={{ animationDelay: "0.6s" }}>
            {analysis.portWeather ? <PortWeatherCard portWeather={analysis.portWeather} /> : <RecommendationsCard recommendations={analysis.recommendations} />}
          </div>
          <div className="animate-fade-up lg:col-span-6" style={{ animationDelay: "0.7s" }}><AgentTimeline events={analysis.agentEvents} /></div>
        </div>
      </div>

      {/* Footer */}
      <div className="animate-fade-up mt-10 flex flex-col items-center justify-between gap-4 rounded-2xl border border-card-border bg-white/[0.02] px-6 py-5 sm:flex-row" style={{ animationDelay: "0.8s" }}>
        <p className="font-mono text-[11px] text-faint">Generated {new Date(analysis.generatedAt).toLocaleTimeString("en-US")} · ClickHouse · Pioneer · TrueFoundry · Langfuse</p>
        <Button asChild size="sm" variant="outline"><Link href="/analyze">Analyze another shipment<ArrowRight /></Link></Button>
      </div>
    </div>
  );
}
