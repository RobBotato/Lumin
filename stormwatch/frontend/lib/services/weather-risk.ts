/**
 * Weather risk analysis service — connects to Lumin backend.
 */
import type { ShipmentInput, WeatherRiskAnalysis } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export class LuminError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = "LuminError";
  }
}

export async function getWeatherRiskAnalysis(
  input: ShipmentInput,
): Promise<WeatherRiskAnalysis> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/api/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        productType: input.productType,
        origin: input.origin,
        destination: input.destination,
        shippingDate: input.shippingDate,
        quantity: input.quantity,
        estimatedWeight: input.estimatedWeight,
        weightUnit: input.weightUnit,
        shipmentValue: input.shipmentValue,
        packagingType: input.packagingType,
        transportMethod: input.transportMethod,
        deliveryPriority: input.deliveryPriority,
        riskTolerance: input.riskTolerance,
        clientPhone: input.clientPhone,
        clientName: input.clientName,
        carrier: input.carrier,
        clientEmail: input.clientEmail,
      }),
    });
  } catch {
    throw new LuminError(
      "Cannot reach the Lumin agent. Make sure the backend is running on port 8080.",
    );
  }

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new LuminError(
      `Lumin API error (${response.status}): ${errorText}`,
      response.status,
    );
  }

  const data = await response.json();

  return {
    shipment: data.shipment,
    riskLevel: data.riskLevel,
    riskScore: data.riskScore,
    confidence: data.confidence,
    summary: data.summary,
    threats: data.threats,
    recommendations: data.recommendations,
    agentEvents: data.agentEvents,
    generatedAt: data.generatedAt,
    safeShippingWindows: data.safeShippingWindows,
    alternativeRoutes: data.alternativeRoutes,
    financialBreakdown: data.financialBreakdown,
    portWeather: data.portWeather,
    historicalComparison: data.historicalComparison,
    executiveSummary: data.executiveSummary,
    businessImpact: data.businessImpact,
    rescheduledTo: data.rescheduledTo,
  };
}
