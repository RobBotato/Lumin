"use client";

import { CalendarCheck, CalendarPlus, Clock, MoveRight } from "lucide-react";
import type { RescheduleInfo, ShipmentInput } from "@/lib/types";

interface Props {
  reschedule: RescheduleInfo;
  shipment: ShipmentInput;
}

export function RescheduleBanner({ reschedule, shipment }: Props) {
  if (!reschedule) return null;

  const calUrl = new URL("http://localhost:8080/api/calendar-event");
  calUrl.searchParams.set("title", shipment.productType);
  calUrl.searchParams.set("date", reschedule.newDate);
  calUrl.searchParams.set("origin", shipment.origin);
  calUrl.searchParams.set("destination", shipment.destination);
  calUrl.searchParams.set("notes", reschedule.reason);

  const formatDate = (iso: string) =>
    new Date(iso + "T12:00:00").toLocaleDateString("en-US", {
      weekday: "short", month: "short", day: "numeric", year: "numeric",
    });

  return (
    <div className="animate-fade-up rounded-2xl border-2 border-accent/30 bg-accent/[0.04] p-6">
      <div className="flex items-start gap-4">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-accent/[0.12]">
          <CalendarCheck className="size-5 text-accent" />
        </div>
        <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-accent">Auto-Rescheduled</span>
              <span className="rounded-full bg-accent/[0.15] px-2 py-0.5 font-mono text-[9px] text-accent">AGENT ACTION</span>
            </div>
            <h3 className="font-display text-lg font-semibold">
              Shipment moved{" "}
              <span className="text-accent">{reschedule.daysMoved} days</span>{" "}
              forward to{" "}
              <span className="text-accent">{reschedule.newDateLabel}</span>
            </h3>
            <p className="mt-1.5 text-sm text-muted leading-relaxed">
              {reschedule.reason}
            </p>
            <p className="mt-1 font-mono text-[10px] text-faint">
              Calendar event updated · Old date cancelled · New invite sent to logistics team
            </p>
        </div>
      </div>

      <div className="mt-5 flex items-center gap-3 pt-4 border-t border-card-border">
        <div className="flex items-center gap-2 font-mono text-xs text-muted">
          <Clock className="size-3 text-faint" />
          <span className="text-faint line-through">{formatDate(reschedule.originalDate)}</span>
          <MoveRight className="size-3 text-accent" />
          <span className="text-accent font-bold">{formatDate(reschedule.newDate)}</span>
        </div>
        <a
          href={calUrl.toString()}
          download
          className="ml-auto inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 font-mono text-xs font-bold text-black shadow-[0_0_20px_-4px_var(--accent)] hover:bg-[#5ff0e4] transition-colors"
        >
          <CalendarPlus className="size-3.5" />
          Add to Calendar
        </a>
      </div>
    </div>
  );
}
