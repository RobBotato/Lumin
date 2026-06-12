"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

export function ScrollRestorer() {
  const pathname = usePathname();

  useEffect(() => {
    // Scroll to top on every route change
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [pathname]);

  return null;
}
