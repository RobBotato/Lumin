/**
 * Core domain types for Lumin.
 *
 * These types form the contract between the UI and the analysis service.
 */

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export const PRODUCT_TYPES = [
  "Vaccines",
  "Electronics",
  "Fresh Produce",
  "Pharmaceuticals",
  "Consumer Goods",
] as const;

export type ProductType = (typeof PRODUCT_TYPES)[number];

export type RiskTolerance = "Conservative" | "Balanced" | "Aggressive";
export type PackagingType = "Standard" | "Refrigerated" | "Waterproof" | "Fragile" | "Hazardous";
export type TransportMethod = "Truck" | "Air" | "Rail" | "Ocean";
export type DeliveryPriority = "Standard" | "Expedited" | "Critical";

export const PACKAGING_TYPES: PackagingType[] = ["Standard", "Refrigerated", "Waterproof", "Fragile", "Hazardous"];
export const TRANSPORT_METHODS: TransportMethod[] = ["Truck", "Air", "Rail", "Ocean"];
export const DELIVERY_PRIORITIES: DeliveryPriority[] = ["Standard", "Expedited", "Critical"];

export interface ShipmentInput {
  productType: string;
  origin: string;
  destination: string;
  shippingDate: string;
  quantity?: number;
  estimatedWeight?: number;
  weightUnit?: "kg" | "lbs";
  shipmentValue?: number;
  packagingType?: PackagingType;
  transportMethod?: TransportMethod;
  deliveryPriority?: DeliveryPriority;
  riskTolerance?: RiskTolerance;
  clientPhone?: string;
  clientName?: string;
  carrier?: string;
  clientEmail?: string;
}

export type ThreatSeverity = "low" | "moderate" | "severe";

export type ThreatIcon = "heat" | "storm" | "humidity" | "rain" | "snow" | "wind";

export interface WeatherThreat {
  id: string;
  label: string;
  severity: ThreatSeverity;
  probability: number;
  detail: string;
  icon: ThreatIcon;
  proximityKm?: number;
  direction?: string | null;
  estimatedLandfall?: string | null;
}

export type RecommendationImpact = "critical" | "recommended" | "optional";

export type RecommendationIcon =
  | "refrigerate"
  | "waterproof"
  | "delay"
  | "monitor"
  | "reroute"
  | "standard";

export interface Recommendation {
  id: string;
  title: string;
  detail: string;
  impact: RecommendationImpact;
  icon: RecommendationIcon;
  estimatedSaving?: number;
}

export interface AgentEvent {
  id: string;
  label: string;
  detail: string;
  timestamp: string;
  durationMs: number;
}

export interface SafeWindow {
  date: string;
  dayLabel: string;
  riskLevel: RiskLevel;
  riskScore: number;
  conditions: string;
  recommended: boolean;
}

export interface AlternativeRoute {
  id: string;
  routeName: string;
  originPort: string;
  destinationPort: string;
  additionalDays: number;
  additionalCost: number;
  riskLevel: RiskLevel;
  description: string;
  vessel: string;
}

export interface FinancialBreakdown {
  cargoValue: number;
  estimatedDelayCost: number;
  demurrageFees: number;
  insuranceExposure: number;
  reroutingCost: number;
  spoilageRisk: number;
  totalAtRisk: number;
  estimatedSavingsIfRerouted: number;
  currency: string;
}

export interface PortConditions {
  portName: string;
  conditions: string;
  temperature: string;
  windSpeed: string;
  visibility: string;
  stormProximity: string;
  status: "operational" | "restricted" | "closed";
}

export interface PortWeather {
  origin: PortConditions;
  destination: PortConditions;
}

export interface HistoricalComparison {
  eventName: string;
  year: string;
  region: string;
  avgDelay: number;
  estimatedCost: number;
  lessons: string;
  similarityScore: number;
}

export interface ExecutiveSummary {
  mainRisks: string[];
  businessImpact: string;
  topRecommendations: string[];
}

export interface BusinessImpact {
  shipmentValue: number;
  estimatedExposure: number;
  operationalImpact: string;
  delayCostPerDay: number;
  confidenceLevel: string;
}

export interface WeatherRiskAnalysis {
  shipment: ShipmentInput;
  riskLevel: RiskLevel;
  riskScore: number;
  confidence: number;
  summary: string;
  threats: WeatherThreat[];
  recommendations: Recommendation[];
  agentEvents: AgentEvent[];
  generatedAt: string;
  safeShippingWindows?: SafeWindow[];
  alternativeRoutes?: AlternativeRoute[];
  financialBreakdown?: FinancialBreakdown;
  portWeather?: PortWeather;
  historicalComparison?: HistoricalComparison | null;
  executiveSummary?: ExecutiveSummary;
  businessImpact?: BusinessImpact;
  rescheduledTo?: RescheduleInfo | null;
}

export interface RescheduleInfo {
  originalDate: string;
  newDate: string;
  newDateLabel: string;
  daysMoved: number;
  reason: string;
  autoRescheduled: boolean;
}
