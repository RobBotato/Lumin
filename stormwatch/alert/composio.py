from config import COMPOSIO_API_KEY


async def send_alert(assessment: dict, threat: dict | None = None):
    channel = "#logistics-alerts"
    risk_level = assessment.get("risk_level", "low")

    if risk_level not in ("high", "critical"):
        return

    summary = assessment.get("summary", "Stormwatch detected a threat.")
    impact = assessment.get("total_financial_impact_usd", 0)
    routes = assessment.get("affected_routes", [])
    recommendation = assessment.get("recommendation", "")

    message = (
        f":warning: *STORMWATCH ALERT — {risk_level.upper()}*\n\n"
        f"{summary}\n\n"
    )
    if impact:
        message += f"*Financial Impact:* ${impact:,.0f}\n"
    if routes:
        vessels = [r.get("vessel_name", "?") for r in routes]
        message += f"*Affected Vessels:* {', '.join(vessels)}\n"
    if recommendation:
        message += f"\n*Recommendation:* {recommendation}\n"

    if COMPOSIO_API_KEY:
        try:
            await _composio_slack(message, channel)
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"SLACK ALERT via Composio → {channel}")
            print(message)
            print(f"{'='*60}\n")
    else:
        print(f"\n{'='*60}")
        print(f"SLACK ALERT → {channel}")
        print(message)
        print(f"{'='*60}\n")


async def _composio_slack(message: str, channel: str):
    # Try new composio SDK first
    try:
        from composio import Composio
        client = Composio(api_key=COMPOSIO_API_KEY)
        result = client.tools.execute(
            action="SLACK_SEND_MESSAGE",
            params={"channel": channel, "text": message},
        )
        print(f"Composio Slack sent: {result}")
        return
    except Exception:
        pass

    # Try old composio-core SDK
    try:
        from composio import ComposioToolSet
        toolset = ComposioToolSet(api_key=COMPOSIO_API_KEY)
        toolset.execute_action(
            action="SLACK_SEND_MESSAGE",
            params={"channel": channel, "text": message},
        )
        print("Composio Slack sent (legacy SDK)")
        return
    except Exception:
        pass

    raise RuntimeError("Composio SDK not available")
