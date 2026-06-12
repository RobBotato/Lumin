# Cargo Insurance Triggers

## Automatic Trigger Conditions
The Stormwatch agent should recommend initiating cargo insurance claims when:

### Immediate Trigger
- Category 3+ weather event within 200km of vessel with cargo value >$5M
- Port closure lasting >48 hours at destination port
- Vessel rerouting adds >7 days to estimated arrival

### Watch Trigger
- Category 2 weather event within 300km of vessel with cargo value >$10M
- Port closure lasting >24 hours at origin port
- Vessel rerouting adds >4 days to estimated arrival

## Historical Insurance Impact
- Early insurance trigger (72h+ before impact): Reduces claim processing time by 40%
- Late trigger (<24h before impact): Average additional cost $200K per vessel
- Pre-negotiated insurance terms reduce disputes by 60%

## Recommended Actions
1. Document weather event details and proximity to vessel
2. Capture vessel position, cargo manifest, and ETA at time of detection
3. Notify insurer with Stormwatch risk assessment as supporting evidence
4. Track vessel deviation and actual delay for claims adjustment
