/**
 * Mock weather risk scenarios for WeatherGuard AI.
 *
 * This is the single source of mock data for the entire app. To integrate a
 * sponsor weather API, replace the lookup in
 * `lib/services/weather-risk.ts` — this file and the UI stay untouched.
 */

import type {
  AgentEvent,
  ProductType,
  Recommendation,
  RiskLevel,
  WeatherThreat,
} from "@/lib/types";

export interface RiskScenario {
  riskLevel: RiskLevel;
  riskScore: number;
  confidence: number;
  summary: string;
  threats: WeatherThreat[];
  recommendations: Recommendation[];
}

/** Agent pipeline steps. Timestamps are stamped at analysis time by the service. */
export const AGENT_PIPELINE: Omit<AgentEvent, "timestamp">[] = [
  {
    id: "received",
    label: "Shipment received",
    detail: "Route, cargo profile, and departure window parsed and validated.",
    durationMs: 240,
  },
  {
    id: "forecast",
    label: "Weather forecast retrieved",
    detail: "72-hour forecast pulled for origin, destination, and 14 route waypoints.",
    durationMs: 620,
  },
  {
    id: "risk",
    label: "Risk factors analyzed",
    detail: "Forecast cells cross-referenced against historical disruption data.",
    durationMs: 540,
  },
  {
    id: "sensitivity",
    label: "Product sensitivity evaluated",
    detail: "Cargo tolerance thresholds matched against expected route conditions.",
    durationMs: 380,
  },
  {
    id: "recommendations",
    label: "Recommendations generated",
    detail: "Mitigation plan ranked by cost-to-impact ratio across 6 strategies.",
    durationMs: 460,
  },
];

export const MOCK_SCENARIOS: Record<ProductType, RiskScenario> = {
  Vaccines: {
    riskLevel: "HIGH",
    riskScore: 84,
    confidence: 94,
    summary:
      "Sustained extreme heat along the route threatens cold-chain integrity. Unmitigated, the temperature excursion probability exceeds acceptable thresholds for biologics.",
    threats: [
      {
        id: "heat",
        label: "Extreme Heat",
        severity: "severe",
        probability: 88,
        detail: "Forecast highs of 41°C (106°F) across 60% of the route corridor.",
        icon: "heat",
      },
      {
        id: "humidity",
        label: "High Humidity",
        severity: "moderate",
        probability: 64,
        detail: "Dew points above 22°C raise condensation risk during transfers.",
        icon: "humidity",
      },
      {
        id: "storms",
        label: "Thunderstorms",
        severity: "moderate",
        probability: 42,
        detail: "Isolated afternoon cells may force unplanned stops near the destination.",
        icon: "storm",
      },
    ],
    recommendations: [
      {
        id: "reefer",
        title: "Use refrigerated transport",
        detail: "Active cooling (2–8°C validated reefer) is required for this corridor and season.",
        impact: "critical",
        icon: "refrigerate",
      },
      {
        id: "monitor",
        title: "Add temperature monitoring",
        detail: "Real-time IoT loggers with 5-minute intervals and excursion alerts.",
        impact: "critical",
        icon: "monitor",
      },
      {
        id: "delay",
        title: "Delay shipment 12 hours",
        detail: "A night departure avoids peak heat through the highest-exposure segment.",
        impact: "recommended",
        icon: "delay",
      },
    ],
  },
  "Fresh Produce": {
    riskLevel: "HIGH",
    riskScore: 76,
    confidence: 91,
    summary:
      "Heat and humidity along the corridor will accelerate spoilage. Heavy rain near the destination adds handling delays at the final transfer point.",
    threats: [
      {
        id: "heat",
        label: "Extreme Heat",
        severity: "severe",
        probability: 79,
        detail: "Trailer temperatures could exceed 45°C during midday segments.",
        icon: "heat",
      },
      {
        id: "humidity",
        label: "High Humidity",
        severity: "moderate",
        probability: 71,
        detail: "Sustained 85%+ relative humidity shortens shelf life by an estimated 30%.",
        icon: "humidity",
      },
      {
        id: "rain",
        label: "Heavy Rain",
        severity: "moderate",
        probability: 56,
        detail: "50mm+ accumulation expected near the destination on arrival day.",
        icon: "rain",
      },
    ],
    recommendations: [
      {
        id: "reefer",
        title: "Use refrigerated transport",
        detail: "Pre-cooled reefer at 4°C with humidity control for leafy and soft produce.",
        impact: "critical",
        icon: "refrigerate",
      },
      {
        id: "delay",
        title: "Delay shipment 12 hours",
        detail: "Shifting departure avoids the peak-heat window across the inland segment.",
        impact: "recommended",
        icon: "delay",
      },
      {
        id: "waterproof",
        title: "Add waterproof packaging",
        detail: "Sealed liners protect cartons during dock transfers in heavy rain.",
        impact: "recommended",
        icon: "waterproof",
      },
    ],
  },
  Pharmaceuticals: {
    riskLevel: "MEDIUM",
    riskScore: 58,
    confidence: 92,
    summary:
      "Humidity and storm activity present moderate excursion risk. Standard mitigations keep this shipment within compliance tolerances.",
    threats: [
      {
        id: "humidity",
        label: "High Humidity",
        severity: "moderate",
        probability: 67,
        detail: "Extended humidity exposure risks packaging integrity for blister packs.",
        icon: "humidity",
      },
      {
        id: "storms",
        label: "Thunderstorms",
        severity: "moderate",
        probability: 48,
        detail: "Storm cells along the mid-route may add 2–4 hours of transit time.",
        icon: "storm",
      },
    ],
    recommendations: [
      {
        id: "monitor",
        title: "Add temperature monitoring",
        detail: "Continuous loggers ensure GDP compliance documentation end-to-end.",
        impact: "critical",
        icon: "monitor",
      },
      {
        id: "waterproof",
        title: "Add waterproof packaging",
        detail: "Desiccant packs and sealed secondary packaging counter humidity exposure.",
        impact: "recommended",
        icon: "waterproof",
      },
      {
        id: "reroute",
        title: "Choose alternate route",
        detail: "The northern corridor avoids the most active storm cells, adding only 40 miles.",
        impact: "optional",
        icon: "reroute",
      },
    ],
  },
  Electronics: {
    riskLevel: "MEDIUM",
    riskScore: 52,
    confidence: 89,
    summary:
      "Heavy rain and storm exposure create moisture risk during dock transfers. Cargo is otherwise tolerant of forecast temperature ranges.",
    threats: [
      {
        id: "rain",
        label: "Heavy Rain",
        severity: "moderate",
        probability: 72,
        detail: "Sustained rainfall forecast across the final third of the route.",
        icon: "rain",
      },
      {
        id: "storms",
        label: "Thunderstorms",
        severity: "moderate",
        probability: 51,
        detail: "Lightning risk may pause loading operations at the destination hub.",
        icon: "storm",
      },
      {
        id: "humidity",
        label: "High Humidity",
        severity: "low",
        probability: 38,
        detail: "Brief humidity spikes — within tolerance for sealed components.",
        icon: "humidity",
      },
    ],
    recommendations: [
      {
        id: "waterproof",
        title: "Add waterproof packaging",
        detail: "Anti-static moisture barrier bags with humidity indicator cards.",
        impact: "critical",
        icon: "waterproof",
      },
      {
        id: "reroute",
        title: "Choose alternate route",
        detail: "Rerouting via the southern interchange avoids the heaviest rainfall band.",
        impact: "recommended",
        icon: "reroute",
      },
      {
        id: "delay",
        title: "Delay shipment 12 hours",
        detail: "Storm system clears the destination hub by early morning.",
        impact: "optional",
        icon: "delay",
      },
    ],
  },
  "Consumer Goods": {
    riskLevel: "LOW",
    riskScore: 22,
    confidence: 96,
    summary:
      "Forecast conditions are favorable across the full route. Only light precipitation is expected, well within standard packaging tolerances.",
    threats: [
      {
        id: "rain",
        label: "Light Rain",
        severity: "low",
        probability: 34,
        detail: "Scattered showers possible near the destination; minimal handling impact.",
        icon: "rain",
      },
      {
        id: "wind",
        label: "Moderate Winds",
        severity: "low",
        probability: 28,
        detail: "Gusts up to 35 km/h — no restrictions for standard trailers.",
        icon: "wind",
      },
    ],
    recommendations: [
      {
        id: "standard",
        title: "Proceed with standard packaging",
        detail: "No special handling required. Current packaging meets all forecast conditions.",
        impact: "recommended",
        icon: "standard",
      },
      {
        id: "waterproof",
        title: "Add waterproof packaging",
        detail: "Optional pallet covers if cargo will stage outdoors at the destination.",
        impact: "optional",
        icon: "waterproof",
      },
    ],
  },
};

/** Fallback scenario when a product type has no dedicated entry. */
export const DEFAULT_SCENARIO: RiskScenario = MOCK_SCENARIOS["Consumer Goods"];
