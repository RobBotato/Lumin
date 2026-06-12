import type { Metadata } from "next";
import { Suspense } from "react";

import { AnalysisView } from "@/components/dashboard/analysis-view";
import { Loader2 } from "lucide-react";

import { SiteHeader } from "@/components/site-header";

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 pb-24 pt-16">
        <Suspense fallback={<div className="flex items-center justify-center py-32"><Loader2 className="size-6 animate-spin text-accent" /></div>}>
          <AnalysisView />
        </Suspense>
      </main>
    </div>
  );
}
