/**
 * Presentation mappings: domain values → visual treatment.
 * Keeps risk/severity/impact styling consistent across the dashboard.
 */

import type { RecommendationImpact, RiskLevel, ThreatSeverity } from "@/lib/types";

export const RISK_META: Record<
  RiskLevel,
  { label: string; color: string; description: string }
> = {
  LOW: {
    label: "Low Risk",
    color: "var(--risk-low)",
    description: "Conditions favorable — proceed as planned",
  },
  MEDIUM: {
    label: "Medium Risk",
    color: "var(--risk-medium)",
    description: "Mitigations advised before departure",
  },
  HIGH: {
    label: "High Risk",
    color: "var(--risk-high)",
    description: "Intervention required to protect cargo",
  },
};

export const SEVERITY_META: Record<
  ThreatSeverity,
  { label: string; badgeVariant: "low" | "medium" | "high" }
> = {
  low: { label: "Low", badgeVariant: "low" },
  moderate: { label: "Moderate", badgeVariant: "medium" },
  severe: { label: "Severe", badgeVariant: "high" },
};

export const IMPACT_META: Record<
  RecommendationImpact,
  { label: string; badgeVariant: "low" | "medium" | "high" | "accent" }
> = {
  critical: { label: "Critical", badgeVariant: "high" },
  recommended: { label: "Recommended", badgeVariant: "accent" },
  optional: { label: "Optional", badgeVariant: "low" },
};
