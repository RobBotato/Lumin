# WeatherGuard AI

**Weather-Aware Logistics Intelligence** — identify shipping risks before they become costly disruptions.

An AI-powered weather risk agent for logistics teams. Enter a shipment, and the agent pulls route forecasts, scores weather risk against the cargo's sensitivity profile, and generates ranked mitigation recommendations.

## Demo flow

1. **Landing** (`/`) — product overview with a live agent console preview
2. **Analyze** (`/analyze`) — enter product type, origin, destination, and shipping date (pre-filled with a sample shipment; preset chips for quick demos)
3. **Dashboard** (`/dashboard`) — watch the agent pipeline execute, then review the risk score, detected threats, AI recommendations, and the agent activity timeline

Tip: each product type produces a different risk profile — **Vaccines** → HIGH, **Electronics** → MEDIUM, **Consumer Goods** → LOW.

## Getting started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Tech stack

- Next.js 15 (App Router) + TypeScript
- Tailwind CSS v4
- shadcn/ui-style components (Radix primitives + CVA)
- Lucide React icons

## Architecture

```
app/
  page.tsx                 Landing page
  analyze/page.tsx         Shipment input
  dashboard/page.tsx       Analysis dashboard
components/
  ui/                      Reusable primitives (button, card, input, select, …)
  landing/                 Landing-page sections
  analyze/                 Shipment form
  dashboard/               Risk score, threats, recommendations, agent timeline
lib/
  types.ts                 Domain types (the UI ↔ service contract)
  mock-data.ts             All mock scenarios, keyed by product type
  services/weather-risk.ts getWeatherRiskAnalysis() — the single integration point
  presentation.ts          Domain → visual mappings (risk colors, badges)
```

## Swapping in a real weather API

The UI only ever calls `getWeatherRiskAnalysis()` in `lib/services/weather-risk.ts`. Replace its body with a sponsor API call that returns a `WeatherRiskAnalysis` (see `lib/types.ts`) — no UI changes required.
