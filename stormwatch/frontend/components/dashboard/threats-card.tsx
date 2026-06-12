import { ScanEye } from "lucide-react";

import { THREAT_ICONS } from "@/components/domain-icons";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SEVERITY_META } from "@/lib/presentation";
import type { WeatherThreat } from "@/lib/types";

interface ThreatsCardProps {
  threats: WeatherThreat[];
}

export function ThreatsCard({ threats }: ThreatsCardProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="space-y-1.5">
          <CardTitle className="flex items-center gap-2">
            <ScanEye className="size-4 text-accent" />
            Threat Detection
          </CardTitle>
          <CardDescription>
            Weather cells intersecting the route corridor
          </CardDescription>
        </div>
        <Badge>
          {threats.length} {threats.length === 1 ? "threat" : "threats"}
        </Badge>
      </CardHeader>

      <CardContent className="space-y-3">
        {threats.map((threat, i) => {
          const Icon = THREAT_ICONS[threat.icon];
          const severity = SEVERITY_META[threat.severity];
          return (
            <div
              key={threat.id}
              className="glass-subtle animate-fade-up rounded-xl p-4"
              style={{ animationDelay: `${0.35 + i * 0.12}s` }}
            >
              <div className="flex items-start gap-3.5">
                <span className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-white/[0.08] bg-white/[0.04]">
                  <Icon className="size-5 text-accent" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-semibold">{threat.label}</p>
                    <Badge variant={severity.badgeVariant}>{severity.label}</Badge>
                    <span className="ml-auto font-mono text-xs text-muted">
                      {threat.probability}%
                    </span>
                  </div>
                  <p className="mt-1 text-[13px] leading-relaxed text-muted">
                    {threat.detail}
                  </p>
                  <div className="mt-2.5 h-1 w-full overflow-hidden rounded-full bg-white/[0.06]">
                    <div
                      className="animate-bar-grow h-full rounded-full"
                      style={{
                        width: `${threat.probability}%`,
                        animationDelay: `${0.5 + i * 0.12}s`,
                        background: `var(--risk-${
                          threat.severity === "severe"
                            ? "high"
                            : threat.severity === "moderate"
                              ? "medium"
                              : "low"
                        })`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
