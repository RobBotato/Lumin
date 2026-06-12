/**
 * Maps serializable icon keys from the data layer to Lucide components.
 * The data layer stays JSON-friendly; only the UI knows about icons.
 */

import {
  Activity,
  CloudLightning,
  CloudRain,
  Droplets,
  type LucideIcon,
  PackageCheck,
  Route,
  Snowflake,
  ThermometerSun,
  Timer,
  Umbrella,
  Wind,
} from "lucide-react";

import type { RecommendationIcon, ThreatIcon } from "@/lib/types";

export const THREAT_ICONS: Record<ThreatIcon, LucideIcon> = {
  heat: ThermometerSun,
  storm: CloudLightning,
  humidity: Droplets,
  rain: CloudRain,
  snow: Snowflake,
  wind: Wind,
};

export const RECOMMENDATION_ICONS: Record<RecommendationIcon, LucideIcon> = {
  refrigerate: Snowflake,
  waterproof: Umbrella,
  delay: Timer,
  monitor: Activity,
  reroute: Route,
  standard: PackageCheck,
};
