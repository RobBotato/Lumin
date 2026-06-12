# ⚡ Lumin — Hackathon Demo Script

**Duration:** ~3 minutes 30 seconds  
**Recording setup:** Screen recording of `localhost:3000`, 1920×1080, clean browser (no bookmarks bar), dark mode

---

## PRE-FLIGHT CHECKLIST (Do this before recording)

```
✓ Backend running:  curl http://localhost:8080/api/health → {"status":"running"}
✓ Frontend running: curl http://localhost:3000 → 200
✓ Google Calendar connected (for the reschedule banner to show)
✓ Close all other tabs and apps
✓ Hide browser bookmarks bar (Cmd+Shift+B in Chrome)
✓ Mute notifications
✓ Test once without recording to make sure flow works
```

---

## SCRIPT

### ACT 1 — The Problem (0:00 – 0:25)

```
[Screen shows the landing page at localhost:3000]
[Speaker voiceover]

SPEAKER:
Every year, weather disruptions cost the global supply chain over
50 billion dollars. A single storm can delay a shipment of vaccines
by days — and when those vaccines need refrigeration, that delay
means millions in spoiled cargo.

Today I'm going to show you Lumin — an AI agent that detects weather
threats before they hit, automatically reschedules your shipments,
and notifies your clients. All in under 5 seconds.

[Click "Analyze Shipment" button to navigate to /analyze]
```

### ACT 2 — The Shipment (0:25 – 0:50)

```
[On the /analyze page]

SPEAKER:
Here's our scenario. We have 2,000 units of vaccines shipping from
Phoenix to Dallas. They're refrigerated, worth 2.5 million dollars,
and the delivery is critical.

[Click the "Vaccines · PHX → DAL" preset chip at the top]

SPEAKER:
I'll use our preset chip to fill everything in instantly.

[Scroll down quickly to show all fields are filled]
[Point at the client email field]

SPEAKER:
I'm also going to add a client email — Lumin will automatically
notify them if anything changes.

[Type "demo@example.com" in client email]
[Hover over the "Analyze Shipment" button]
```

### ACT 3 — The Agent Pipeline (0:50 – 1:40)

```
[Click "Analyze Shipment" — redirects to /dashboard]

SPEAKER:
Watch what happens. The agent pipeline kicks in immediately.

[Watch the loading console do its animated steps]

SPEAKER:
Step by step, Lumin is —
1. Matching our route to known shipping corridors
2. Ingesting real-time weather data from ClickHouse
3. Detecting a tropical storm 45 kilometers from our route
4. Extracting storm details — name, category, wind speed — using NLP
5. Querying its knowledge base for historical disruption patterns
6. And finally, asking the LLM to assess the risk

[Agent events start appearing]

SPEAKER:
There it is. Risk level: HIGH. 74 out of 100 on our multi-factor
risk score. Confidence: 55%.

Let me break down what it found.
```

### ACT 4 — The Dashboard (1:40 – 2:25)

```
[Scroll down through the dashboard]

SPEAKER:
First, the risk score card. This isn't just an LLM guess — it's a
mathematical model factoring in wind speed, storm proximity, cargo
sensitivity, and route exposure. All weighted by your risk tolerance.

[Point to ThreatsCard]

SPEAKER:
Four threats detected — the storm itself, high winds exceeding
container stacking limits, heavy precipitation risking port delays,
and elevated humidity threatening cold chain integrity.

[Scroll to RecommendationsCard]

SPEAKER:
Three ranked recommendations. The top one is critical — reroute
via an alternate corridor. Saves an estimated $2.8 million.
There's also a delay option and a packaging upgrade.

[Scroll to AlternativeRoutesCard]

SPEAKER:
Alternative routes with trade-offs — southern corridor bypass
adds 3 days but zero weather exposure. Rail intermodal is faster
but more expensive. And a hold-and-sprint window for the brave.
```

### ACT 5 — Auto-Reschedule & Calendar (2:25 – 2:55)

```
[Scroll to RescheduleBanner]

SPEAKER:
But here's where it gets really cool. Lumin automatically found a
safe shipping window and rescheduled the shipment.

[Point at the dates]

SPEAKER:
Original date — June 15th. New date — June 19th. Four days forward.

[Point at the agent timeline at the bottom]

SPEAKER:
The agent timeline shows absolutely everything. Step 6 — calendar
event cancelled, step 7 — new calendar event created, and step 8 —
email notification sent to the client.

[Scroll up to show the reschedule banner again]

SPEAKER:
The old date is crossed out on Google Calendar. The new date has a
fresh event. And the client just got this email.

[Quickly switch to Gmail tab to show the formatted email]
[Switch back to the dashboard]
```

### ACT 6 — The Tech & Impact (2:55 – 3:30)

```
[Pull up the architecture slide or just talk over the dashboard footer]

SPEAKER:
Under the hood, this is a FastAPI backend on top of ClickHouse
for analytical queries. We use Langfuse for complete LLM
observability — every prompt, every response, every token is traced.
Google Calendar OAuth2 for calendar sync. Pioneer for NLP entity
extraction. And the frontend is Next.js 15 with real-time WebSocket
updates.

SPEAKER:
The result? Instead of discovering a disrupted shipment when it's
already late, your logistics team gets an automatic reschedule,
a calendar update, and the client is notified — before anyone
even checks the weather report.

SPEAKER:
Lumin turns supply chain weather risk from a reactive crisis into
a proactive workflow. Thank you.

[End on the dashboard showing the full view]
```

---

## QUICK REFERENCE — What to show on screen

| Time  | Screen |
|-------|--------|
| 0:00  | Landing page |
| 0:25  | `/analyze` page, click "Vaccines · PHX → DAL" preset, type email |
| 0:50  | Click "Analyze Shipment" → watch agent pipeline animate |
| 1:40  | Scroll through Risk Score → Threats → Recommendations → Alternative Routes |
| 2:25  | Show Reschedule Banner with dates, agent timeline steps 6-8 |
| 2:45  | Switch to Gmail tab — show the email |
| 2:55  | Talk over dashboard, end on full view |

---

## TIPS

- **Speak slightly faster than normal** — hackathon judges are tired, energy wins
- **Don't read every data point** — point at it and summarize
- **If something breaks**, keep talking. The judges won't notice a half-second delay
- **Remember the preset chip** — "Vaccines · PHX → DAL" is the most dramatic scenario
- **The email is auto-sent to whatever you type** — use your own email to actually see it
