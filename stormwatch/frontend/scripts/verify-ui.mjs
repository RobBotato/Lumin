import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = "http://localhost:3100";
const OUT = "scripts/shots";
mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

const consoleErrors = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text());
});
page.on("pageerror", (err) => consoleErrors.push(`pageerror: ${err.message}`));

// 1. Landing page
await page.goto(`${BASE}/`);
await page.waitForTimeout(4000);
await page.screenshot({ path: `${OUT}/01-landing.png`, fullPage: true });
console.log("landing h1:", await page.locator("h1").innerText());

// 2. Navigate via header CTA
await page.getByRole("link", { name: /Analyze Shipment/i }).first().click();
await page.waitForURL("**/analyze");
await page.waitForTimeout(1200);
await page.screenshot({ path: `${OUT}/02-analyze.png`, fullPage: true });

// 3. Apply Electronics preset, then submit
await page.getByRole("button", { name: /Electronics · SEA/ }).click();
console.log("origin after preset:", await page.locator("#origin").inputValue());
await page.getByRole("button", { name: /^Analyze Shipment$/ }).click();
await page.waitForURL("**/dashboard**");

// 4. Capture the agent console mid-run
await page.waitForTimeout(1100);
await page.screenshot({ path: `${OUT}/03-loading-console.png` });

// 5. Wait for results reveal
await page.waitForSelector("text=Risk analysis complete", { timeout: 10000 });
await page.waitForTimeout(2500);
await page.screenshot({ path: `${OUT}/04-dashboard-electronics.png`, fullPage: true });
console.log("dashboard url:", page.url());
console.log("risk badge:", await page.locator("text=MEDIUM").count(), "MEDIUM elements");

// 6. Probe: garbage product type + missing params -> should fall back gracefully
await page.goto(`${BASE}/dashboard?product=__nope__&origin=&date=not-a-date`);
await page.waitForSelector("text=Risk analysis complete", { timeout: 10000 });
await page.waitForTimeout(2000);
await page.screenshot({ path: `${OUT}/05-dashboard-fallback.png`, fullPage: true });
const fallbackHeading = await page.locator("h1").innerText();
console.log("fallback heading:", fallbackHeading.replace(/\n/g, " | "));

// 7. Probe: direct dashboard hit with HIGH-risk product
await page.goto(
  `${BASE}/dashboard?product=Vaccines&origin=Phoenix%2C%20AZ&destination=Dallas%2C%20TX&date=2026-06-14`,
);
await page.waitForSelector("text=Risk analysis complete", { timeout: 10000 });
await page.waitForTimeout(2500);
await page.screenshot({ path: `${OUT}/06-dashboard-vaccines.png`, fullPage: true });
console.log("vaccines HIGH count:", await page.locator("text=HIGH").count());

// 8. Mobile viewport check
await page.setViewportSize({ width: 390, height: 844 });
await page.goto(`${BASE}/`);
await page.waitForTimeout(3000);
await page.screenshot({ path: `${OUT}/07-landing-mobile.png`, fullPage: true });

console.log("console errors:", consoleErrors.length ? consoleErrors : "none");
await browser.close();
