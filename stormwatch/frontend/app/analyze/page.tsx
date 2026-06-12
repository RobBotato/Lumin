import type { Metadata } from "next";

import { ShipmentForm } from "@/components/analyze/shipment-form";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: "New Analysis — Lumin",
};

export default function AnalyzePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-2xl flex-1 px-6 pb-24 pt-16">
        <div className="animate-fade-up">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">
            Step 1 of 2 — Shipment details
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold tracking-tight">
            What are you shipping?
          </h1>
          <p className="mt-3 text-muted">
            The agent will pull route forecasts and score weather risk against your cargo profile.
          </p>
        </div>
        <ShipmentForm />
      </main>
    </div>
  );
}
