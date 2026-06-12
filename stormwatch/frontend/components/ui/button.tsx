import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/60 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-accent text-accent-foreground shadow-[0_0_24px_-6px_var(--accent)] hover:bg-[#5ff0e4] hover:shadow-[0_0_36px_-6px_var(--accent)] active:scale-[0.98]",
        outline:
          "border border-card-border bg-white/[0.03] text-foreground backdrop-blur-sm hover:bg-white/[0.07] hover:border-white/20 active:scale-[0.98]",
        ghost: "text-muted hover:text-foreground hover:bg-white/[0.05]",
      },
      size: {
        default: "h-10 px-5 text-sm [&_svg]:size-4",
        sm: "h-8 px-3.5 text-xs [&_svg]:size-3.5",
        lg: "h-12 px-7 text-base [&_svg]:size-4.5",
        xl: "h-14 px-9 text-base [&_svg]:size-5",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size }), className)}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
