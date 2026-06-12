# Delay Notification Standard Operating Procedure

## Alert Severity Tiers

### CRITICAL (Risk Level)
- Trigger: Category 3+ weather event within 200km of active vessel with cargo >$10M
- Action: Immediate Slack alert (#logistics-alerts) + email to ops@ within 30 seconds
- Content: Full risk assessment, affected routes, financial impact, recommended action
- Escalation: If no acknowledgment within 5 minutes, escalate to logistics director
- Historical pattern: 85% of critical alerts result in rerouting action

### HIGH (Risk Level)
- Trigger: Category 2+ weather event within 300km of active vessel
- Action: Slack alert (#logistics-alerts) within 60 seconds
- Content: Risk summary, affected routes, recommended action
- Escalation: If no action within 30 minutes, email ops@
- Historical pattern: 60% of high alerts result in preventive action

### MEDIUM (Risk Level)
- Trigger: Severe weather within 500km of active vessel
- Action: Log to daily digest, no immediate alert
- Content: Brief summary in daily operations report
- Escalation: Monitor for 24h; escalate if severity increases
- Historical pattern: 20% of medium events escalate within 24h

### LOW (Risk Level)
- Trigger: Moderate weather, no immediate threat to shipping lanes
- Action: Log only, no notification
- Content: Included in weekly summary report
