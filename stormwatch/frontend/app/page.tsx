import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  CloudSun,
  Radar,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import { HeroConsole } from "@/components/landing/hero-console";
import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";

const STATS = [
  { value: "12,480", label: "Shipments monitored" },
  { value: "$4.2M", label: "Losses prevented" },
  { value: "38", label: "Active weather cells" },
  { value: "99.2%", label: "Forecast uptime" },
] as const;

const FEATURES = [
  {
    icon: CloudSun,
    title: "Forecast ingestion",
    description:
      "Hyperlocal forecasts pulled for every waypoint on your route — 72 hours out, refreshed continuously.",
  },
  {
    icon: BrainCircuit,
    title: "Agentic risk scoring",
    description:
      "An AI agent cross-references weather cells with your cargo's sensitivity profile and historical disruption data.",
  },
  {
    icon: ShieldCheck,
    title: "Actionable mitigations",
    description:
      "Ranked recommendations — reroute, delay, repack — scored by cost-to-impact before your shipment leaves the dock.",
  },
] as const;

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />

      <main className="flex-1">
        {/* ---------- Hero ---------- */}
        <section className="relative mx-auto grid max-w-6xl items-center gap-14 px-6 pb-24 pt-20 lg:grid-cols-[1.05fr_0.95fr] lg:gap-10 lg:pt-28">
          {/* radar rings */}
          <div
            aria-hidden
            className="pointer-events-none absolute -top-32 left-1/2 -z-10 size-[640px] -translate-x-1/2 lg:left-[24%]"
          >
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="absolute inset-0 rounded-full border border-accent/15 [animation:radar-pulse_4.5s_ease-out_infinite]"
                style={{ animationDelay: `${i * 1.5}s` }}
              />
            ))}
          </div>

          <div>
            <div
              className="animate-fade-up inline-flex items-center gap-2 rounded-full border border-accent/25 bg-accent/[0.07] px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-accent"
              style={{ animationDelay: "0.05s" }}
            >
              <Sparkles className="size-3" />
              Agentic weather intelligence
            </div>

            <h1
              className="animate-fade-up mt-6 font-display text-5xl font-semibold leading-[1.04] tracking-tight sm:text-6xl lg:text-[68px]"
              style={{ animationDelay: "0.15s" }}
            >
              Weather-Aware
              <br />
              Logistics{" "}
              <span className="bg-gradient-to-r from-accent via-sky-400 to-accent bg-clip-text text-transparent">
                Intelligence
              </span>
            </h1>

            <p
              className="animate-fade-up mt-6 max-w-md text-lg leading-relaxed text-muted"
              style={{ animationDelay: "0.25s" }}
            >
              Identify shipping risks before they become costly disruptions.
            </p>

            <div
              className="animate-fade-up mt-9 flex flex-wrap items-center gap-4"
              style={{ animationDelay: "0.35s" }}
            >
              <Button asChild size="xl" className="font-display font-semibold">
                <Link href="/analyze">
                  Analyze Shipment
                  <ArrowRight />
                </Link>
              </Button>
              <Button asChild variant="outline" size="xl">
                <Link href="/analyze">Run sample analysis</Link>
              </Button>
            </div>

            <p
              className="animate-fade-up mt-8 font-mono text-xs text-faint"
              style={{ animationDelay: "0.45s" }}
            >
              Trusted by logistics teams moving sensitive cargo across 6 continents
            </p>
          </div>

          <div className="animate-fade-up" style={{ animationDelay: "0.3s" }}>
            <HeroConsole />
          </div>
        </section>

        {/* ---------- Stats ---------- */}
        <section className="border-y border-white/[0.06] bg-white/[0.015]">
          <div className="mx-auto grid max-w-6xl grid-cols-2 divide-white/[0.06] px-6 md:grid-cols-4 md:divide-x">
            {STATS.map((stat, i) => (
              <div
                key={stat.label}
                className="animate-fade-up px-2 py-8 text-center md:py-10"
                style={{ animationDelay: `${0.1 + i * 0.08}s` }}
              >
                <p className="font-display text-3xl font-semibold tracking-tight text-foreground md:text-4xl">
                  {stat.value}
                </p>
                <p className="mt-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-faint">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ---------- Features ---------- */}
        <section className="mx-auto max-w-6xl px-6 py-24">
          <div className="mb-14 max-w-xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-accent">
              How it works
            </p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              From forecast to decision in seconds
            </h2>
          </div>

          <div className="grid gap-5 md:grid-cols-3">
            {FEATURES.map((feature, i) => (
              <div
                key={feature.title}
                className="glass group relative overflow-hidden rounded-2xl p-7 transition-all duration-300 hover:-translate-y-1 hover:border-accent/25"
              >
                <div
                  aria-hidden
                  className="pointer-events-none absolute -right-12 -top-12 size-40 rounded-full bg-accent/[0.06] blur-2xl transition-opacity opacity-0 group-hover:opacity-100"
                />
                <span className="font-mono text-xs text-faint">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div className="mt-5 flex size-11 items-center justify-center rounded-xl border border-accent/20 bg-accent/[0.08]">
                  <feature.icon className="size-5 text-accent" />
                </div>
                <h3 className="mt-5 font-display text-lg font-semibold tracking-tight">
                  {feature.title}
                </h3>
                <p className="mt-2.5 text-sm leading-relaxed text-muted">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </section>

        {/* ---------- CTA band ---------- */}
        <section className="mx-auto max-w-6xl px-6 pb-28">
          <div className="glass relative overflow-hidden rounded-3xl px-8 py-16 text-center md:py-20">
            <div
              aria-hidden
              className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_80%_at_50%_120%,rgba(56,225,212,0.12),transparent_70%)]"
            />
            <Radar className="mx-auto size-8 text-accent" />
            <h2 className="mx-auto mt-5 max-w-2xl font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              Know what the weather will cost you — before it does
            </h2>
            <p className="mx-auto mt-4 max-w-md text-muted">
              Run a full risk analysis on your next shipment in under 30 seconds.
            </p>
            <Button asChild size="xl" className="mt-9 font-display font-semibold">
              <Link href="/analyze">
                Analyze Shipment
                <ArrowRight />
              </Link>
            </Button>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/[0.06] py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 font-mono text-[11px] text-faint sm:flex-row">
          <span>© 2026 Lumin</span>
          <span>Forecast data: demo environment · sponsor API ready</span>
        </div>
      </footer>
    </div>
  );
}
