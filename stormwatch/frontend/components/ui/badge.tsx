import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-medium uppercase tracking-wide transition-colors",
  {
    variants: {
      variant: {
        default: "border-card-border bg-white/[0.04] text-muted",
        accent: "border-accent/30 bg-accent/10 text-accent",
        low: "border-risk-low/30 bg-risk-low/10 text-risk-low",
        medium: "border-risk-medium/30 bg-risk-medium/10 text-risk-medium",
        high: "border-risk-high/30 bg-risk-high/10 text-risk-high",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
