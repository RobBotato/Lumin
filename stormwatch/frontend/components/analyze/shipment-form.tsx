"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CalendarDays, DollarSign, Loader2, MapPin, Navigation, Package, Scale, Hash, Box, Truck, AlertTriangle, Mail, User } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DatePicker } from "@/components/ui/date-picker";
import { RiskToleranceSlider } from "@/components/analyze/risk-tolerance-slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PACKAGING_TYPES, TRANSPORT_METHODS, DELIVERY_PRIORITIES, type PackagingType, type TransportMethod, type DeliveryPriority, type RiskTolerance, type ShipmentInput } from "@/lib/types";

interface Preset { label: string; input: Omit<ShipmentInput, "shippingDate">; }

const PRESETS: Preset[] = [
  { label: "Vaccines · PHX → DAL", input: { productType: "Vaccines", origin: "Phoenix, AZ", destination: "Dallas, TX", quantity: 2000, estimatedWeight: 450, weightUnit: "kg", shipmentValue: 2500000, packagingType: "Refrigerated", transportMethod: "Truck", deliveryPriority: "Critical", riskTolerance: "Balanced" } },
  { label: "Electronics · SEA → CHI", input: { productType: "Electronics", origin: "Seattle, WA", destination: "Chicago, IL", quantity: 500, estimatedWeight: 1200, weightUnit: "kg", shipmentValue: 1800000, packagingType: "Waterproof", transportMethod: "Rail", deliveryPriority: "Expedited", riskTolerance: "Balanced" } },
  { label: "Fresh Produce · MIA → ATL", input: { productType: "Fresh Produce", origin: "Miami, FL", destination: "Atlanta, GA", quantity: 3500, estimatedWeight: 2800, weightUnit: "kg", shipmentValue: 420000, packagingType: "Refrigerated", transportMethod: "Truck", deliveryPriority: "Critical", riskTolerance: "Balanced" } },
];

const SUGGESTIONS = ["Vaccines", "Electronics", "Fresh Produce", "Pharmaceuticals", "Consumer Goods", "Auto Parts", "Medical Devices", "Textiles", "Furniture", "Industrial Equipment", "Perishable Foods", "Chemicals", "Semiconductors", "Steel", "Paper Products", "Glassware"];

function defaultShippingDate(): string { const date = new Date(); date.setDate(date.getDate() + 2); return date.toISOString().slice(0, 10); }

export function ShipmentForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = React.useState(false);
  const [showSuggestions, setShowSuggestions] = React.useState(false);
  const [form, setForm] = React.useState<ShipmentInput>({
    productType: "Electronics", origin: "Seattle, WA", destination: "Chicago, IL", shippingDate: defaultShippingDate(),
    quantity: 500, estimatedWeight: 1200, weightUnit: "kg", shipmentValue: 1800000, packagingType: "Waterproof", transportMethod: "Rail", deliveryPriority: "Expedited", riskTolerance: "Balanced",     clientPhone: "", clientName: "", clientEmail: "",
  });

  const filteredSuggestions = SUGGESTIONS.filter((s) => s.toLowerCase().includes(form.productType.toLowerCase())).filter((s) => s.toLowerCase() !== form.productType.toLowerCase());
  const isValid = form.productType.trim().length > 0 && form.origin.trim().length > 0 && form.destination.trim().length > 0 && form.shippingDate.length > 0;

  function applyPreset(preset: Preset) { setForm((prev) => ({ ...prev, ...preset.input })); }
  function updateField<K extends keyof ShipmentInput>(key: K, value: ShipmentInput[K]) { setForm((prev) => ({ ...prev, [key]: value })); }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!isValid || submitting) return;
    setSubmitting(true);
    const params = new URLSearchParams({ product: form.productType.trim(), origin: form.origin.trim(), destination: form.destination.trim(), date: form.shippingDate });
    if (form.quantity) params.set("quantity", String(form.quantity));
    if (form.estimatedWeight) params.set("weight", String(form.estimatedWeight));
    if (form.weightUnit) params.set("weightUnit", form.weightUnit);
    if (form.shipmentValue) params.set("value", String(form.shipmentValue));
    if (form.packagingType) params.set("packaging", form.packagingType);
    if (form.transportMethod) params.set("transport", form.transportMethod);
    if (form.deliveryPriority) params.set("priority", form.deliveryPriority);
    if (form.riskTolerance) params.set("tolerance", form.riskTolerance);
    if (form.clientName) params.set("clientName", form.clientName);
    if (form.clientEmail) params.set("clientEmail", form.clientEmail);
    router.push(`/dashboard?${params.toString()}`);
  }

  return (
    <form onSubmit={handleSubmit} className="mt-10">
      <div className="animate-fade-up flex flex-wrap gap-2" style={{ animationDelay: "0.1s" }}>
        {PRESETS.map((preset) => (
          <button key={preset.label} type="button" onClick={() => applyPreset(preset)} className="rounded-full border border-card-border bg-white/[0.03] px-3.5 py-1.5 font-mono text-[11px] text-muted transition-all hover:border-accent/40 hover:text-accent">
            {preset.label}
          </button>
        ))}
      </div>

      <div className="glass animate-fade-up mt-5 space-y-6 rounded-2xl p-7 sm:p-8" style={{ animationDelay: "0.18s" }}>
        <div className="grid gap-6 sm:grid-cols-[1fr_140px]">
          <div className="space-y-2.5 relative">
            <Label htmlFor="product-type" className="flex items-center gap-1.5"><Package className="size-3.5" />What are you shipping?</Label>
            <Input id="product-type" placeholder="Type anything — e.g. Semiconductors..." value={form.productType} onChange={(e) => { updateField("productType", e.target.value); setShowSuggestions(true); }} onFocus={() => setShowSuggestions(true)} onBlur={() => setTimeout(() => setShowSuggestions(false), 200)} required autoComplete="off" />
            {showSuggestions && filteredSuggestions.length > 0 && form.productType.length > 0 && (
              <div className="absolute left-0 top-full z-50 mt-1 w-full animate-scale-in origin-top">
                <div className="rounded-xl border border-white/[0.08] bg-[#0d1520] backdrop-blur-2xl shadow-2xl overflow-hidden">
                  {filteredSuggestions.slice(0, 5).map((s) => (
                    <button key={s} type="button" onMouseDown={(e) => { e.preventDefault(); updateField("productType", s); setShowSuggestions(false); }} className="flex w-full items-center gap-2 px-4 py-2.5 text-left font-mono text-xs text-muted hover:bg-white/[0.06] hover:text-foreground transition-colors">{s}</button>
                  ))}
                </div>
              </div>
            )}
          </div>
          <div className="space-y-2.5">
            <Label htmlFor="quantity" className="flex items-center gap-1.5"><Hash className="size-3.5" />Qty</Label>
            <Input id="quantity" type="number" min="1" placeholder="500" value={form.quantity ?? ""} onChange={(e) => updateField("quantity", parseInt(e.target.value) || undefined)} />
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-2.5">
            <Label htmlFor="origin" className="flex items-center gap-1.5"><MapPin className="size-3.5" />Origin</Label>
            <Input id="origin" placeholder="e.g. Shanghai, CN" value={form.origin} onChange={(e) => updateField("origin", e.target.value)} required />
          </div>
          <div className="space-y-2.5">
            <Label htmlFor="destination" className="flex items-center gap-1.5"><Navigation className="size-3.5" />Destination</Label>
            <Input id="destination" placeholder="e.g. Los Angeles, CA" value={form.destination} onChange={(e) => updateField("destination", e.target.value)} required />
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-2.5">
            <Label htmlFor="weight" className="flex items-center gap-1.5"><Scale className="size-3.5" />Estimated Weight</Label>
            <div className="flex gap-2">
              <Input id="weight" type="number" min="0" step="0.1" placeholder="1200" value={form.estimatedWeight ?? ""} onChange={(e) => updateField("estimatedWeight", parseFloat(e.target.value) || undefined)} className="flex-1" />
              <Select value={form.weightUnit ?? "kg"} onValueChange={(v) => updateField("weightUnit", v as "kg" | "lbs")}>
                <SelectTrigger className="w-[80px]"><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="kg">kg</SelectItem><SelectItem value="lbs">lbs</SelectItem></SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2.5">
            <Label htmlFor="value" className="flex items-center gap-1.5"><DollarSign className="size-3.5" />Shipment Value ($)</Label>
            <Input id="value" type="number" min="0" step="100" placeholder="1,800,000" value={form.shipmentValue ?? ""} onChange={(e) => updateField("shipmentValue", parseInt(e.target.value) || undefined)} />
          </div>
        </div>

        <div className="grid gap-6 sm:grid-cols-3">
          <div className="space-y-2.5">
            <Label className="flex items-center gap-1.5"><Box className="size-3.5" />Packaging</Label>
            <Select value={form.packagingType ?? "Standard"} onValueChange={(v) => updateField("packagingType", v as PackagingType)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{PACKAGING_TYPES.map((t) => (<SelectItem key={t} value={t}>{t}</SelectItem>))}</SelectContent>
            </Select>
          </div>
          <div className="space-y-2.5">
            <Label className="flex items-center gap-1.5"><Truck className="size-3.5" />Transport</Label>
            <Select value={form.transportMethod ?? "Truck"} onValueChange={(v) => updateField("transportMethod", v as TransportMethod)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{TRANSPORT_METHODS.map((t) => (<SelectItem key={t} value={t}>{t}</SelectItem>))}</SelectContent>
            </Select>
          </div>
          <div className="space-y-2.5">
            <Label className="flex items-center gap-1.5"><AlertTriangle className="size-3.5" />Priority</Label>
            <Select value={form.deliveryPriority ?? "Standard"} onValueChange={(v) => updateField("deliveryPriority", v as DeliveryPriority)}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>{DELIVERY_PRIORITIES.map((t) => (<SelectItem key={t} value={t}>{t}</SelectItem>))}</SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2.5">
          <Label htmlFor="shipping-date" className="flex items-center gap-1.5"><CalendarDays className="size-3.5" />Shipping Date</Label>
          <DatePicker id="shipping-date" value={form.shippingDate} onChange={(v) => updateField("shippingDate", v)} />
        </div>

        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-2.5">
            <Label htmlFor="client-name" className="flex items-center gap-1.5"><User className="size-3.5" />Client Name</Label>
            <Input id="client-name" placeholder="e.g. Jane Smith" value={form.clientName ?? ""} onChange={(e) => updateField("clientName", e.target.value)} />
          </div>
          <div className="space-y-2.5">
            <Label htmlFor="client-email" className="flex items-center gap-1.5"><Mail className="size-3.5" />Client Email</Label>
            <Input id="client-email" type="email" placeholder="jane@example.com" value={form.clientEmail ?? ""} onChange={(e) => updateField("clientEmail", e.target.value)} />
          </div>
        </div>

        <RiskToleranceSlider value={form.riskTolerance ?? "Balanced"} onChange={(v) => updateField("riskTolerance", v as RiskTolerance)} />

        <Button type="submit" size="xl" disabled={!isValid || submitting} className="w-full font-display font-semibold">
          {submitting ? (<><Loader2 className="animate-spin" />Dispatching agent…</>) : (<>Analyze Shipment<ArrowRight /></>)}
        </Button>

        <p className="text-center font-mono text-[11px] text-faint">All fields optional except product, origin &amp; destination.</p>
      </div>

      {/* Shipment Summary Card — live updating */}
      <div className="glass animate-fade-up mt-6 rounded-2xl p-6" style={{ animationDelay: "0.28s" }}>
        <div className="flex items-center justify-between mb-4">
          <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-accent">Shipment Summary</span>
          <button type="button" onClick={() => window.print()} className="font-mono text-[10px] text-faint hover:text-foreground transition-colors">Export Report</button>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div><span className="font-mono text-[9px] uppercase text-faint">Product</span><p className="font-display text-sm font-semibold">{form.productType || "—"}</p></div>
          <div><span className="font-mono text-[9px] uppercase text-faint">Route</span><p className="font-mono text-xs">{form.origin || "—"} → {form.destination || "—"}</p></div>
          <div><span className="font-mono text-[9px] uppercase text-faint">Date</span><p className="font-mono text-xs">{form.shippingDate ? new Date(form.shippingDate+"T12:00:00").toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"}) : "—"}</p></div>
          <div><span className="font-mono text-[9px] uppercase text-faint">Priority</span><p className="font-mono text-xs font-bold" style={{color:form.deliveryPriority==="Critical"?"var(--pink)":form.deliveryPriority==="Expedited"?"var(--orange)":"var(--muted)"}}>{form.deliveryPriority || "Standard"}</p></div>
        </div>
        {(form.quantity || form.estimatedWeight || form.shipmentValue) && (
          <div className="flex flex-wrap gap-x-6 gap-y-1 mt-3 pt-3 border-t border-card-border">
            {form.quantity && <span className="font-mono text-[10px] text-faint">×{form.quantity.toLocaleString()} units</span>}
            {form.estimatedWeight && <span className="font-mono text-[10px] text-faint">{form.estimatedWeight.toLocaleString()} {form.weightUnit||"kg"}</span>}
            {form.shipmentValue && <span className="font-mono text-[10px] text-faint">${form.shipmentValue.toLocaleString()}</span>}
          </div>
        )}
        <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-card-border">
          {form.packagingType && <span className="rounded-full border border-card-border bg-white/[0.04] px-2 py-0.5 font-mono text-[9px] text-muted">{form.packagingType}</span>}
          {form.transportMethod && <span className="rounded-full border border-card-border bg-white/[0.04] px-2 py-0.5 font-mono text-[9px] text-muted">{form.transportMethod}</span>}
          {form.riskTolerance && <span className="rounded-full border border-accent/25 bg-accent/[0.08] px-2 py-0.5 font-mono text-[9px] text-accent">{form.riskTolerance}</span>}
        </div>
      </div>
    </form>
  );
}
