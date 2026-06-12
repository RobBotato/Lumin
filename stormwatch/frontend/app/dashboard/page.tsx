import type { Metadata } from "next";
import { Suspense } from "react";

import { AnalysisView } from "@/components/dashboard/analysis-view";
import { SiteHeader } from "@/components/site-header";

export const metadata: Metadata = {
  title: "Risk Analysis — Lumin",
};

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-6xl flex-1 px-6 pb-24 pt-16">
        <Suspense>
          <AnalysisView />
        </Suspense>
      </main>
    </div>
  );
}
