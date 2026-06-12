import { Lightbulb } from "lucide-react";

import { RECOMMENDATION_ICONS } from "@/components/domain-icons";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { IMPACT_META } from "@/lib/presentation";
import type { Recommendation } from "@/lib/types";

interface RecommendationsCardProps {
  recommendations: Recommendation[];
}

export function RecommendationsCard({ recommendations }: RecommendationsCardProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex-row items-center justify-between space-y-0">
        <div className="space-y-1.5">
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="size-4 text-accent" />
            AI Recommendations
          </CardTitle>
          <CardDescription>
            Mitigations ranked by cost-to-impact ratio
          </CardDescription>
        </div>
        <Badge variant="accent">Ranked</Badge>
      </CardHeader>

      <CardContent className="space-y-3">
        {recommendations.map((rec, i) => {
          const Icon = RECOMMENDATION_ICONS[rec.icon];
          const impact = IMPACT_META[rec.impact];
          return (
            <div
              key={rec.id}
              className="glass-subtle animate-fade-up group flex items-start gap-4 rounded-xl p-4 transition-colors hover:border-accent/25"
              style={{ animationDelay: `${0.45 + i * 0.12}s` }}
            >
              <span className="pt-0.5 font-mono text-xs text-faint">
                {String(i + 1).padStart(2, "0")}
              </span>
              <span className="flex size-10 shrink-0 items-center justify-center rounded-lg border border-accent/20 bg-accent/[0.08]">
                <Icon className="size-5 text-accent" />
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold">{rec.title}</p>
                  <Badge variant={impact.badgeVariant}>{impact.label}</Badge>
                </div>
                <p className="mt-1 text-[13px] leading-relaxed text-muted">{rec.detail}</p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
