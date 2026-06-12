import type { Metadata } from "next";
import { Bricolage_Grotesque, IBM_Plex_Mono, Instrument_Sans } from "next/font/google";
import { ScrollRestorer } from "@/components/scroll-restorer";
import "./globals.css";

const bricolage = Bricolage_Grotesque({ variable: "--font-bricolage", subsets: ["latin"] });
const instrument = Instrument_Sans({ variable: "--font-instrument", subsets: ["latin"] });
const plexMono = IBM_Plex_Mono({ variable: "--font-plex-mono", subsets: ["latin"], weight: ["400", "500"] });

export const metadata: Metadata = {
  title: "Lumin — AI-Powered Supply Chain Intelligence",
  description:
    "Lumin: AI-powered supply chain risk intelligence. Autonomous detection of weather threats to shipping routes.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" style={{ scrollBehavior: "smooth" }} data-scroll-behavior="smooth">
      <body className={`${bricolage.variable} ${instrument.variable} ${plexMono.variable} antialiased`}>
        <div className="atmosphere" aria-hidden />
        <div className="grid-overlay" aria-hidden />
        <div className="noise-overlay" aria-hidden />
        <ScrollRestorer />
        {children}
      </body>
    </html>
  );
}
