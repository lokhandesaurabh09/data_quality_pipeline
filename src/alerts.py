import json
import urllib.request
from src.logger import setup_logger

logger = setup_logger("alerts")

EMOJI_MAP = {
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "FAILURE": "🚨",
    "INFO": "ℹ️"
}

COLOR_MAP = {
    "SUCCESS": "#36a64f",
    "WARNING": "#ffcc00",
    "FAILURE": "#ff0000",
    "INFO": "#439FE0"
}

def send_webhook_alert(webhook_url: str, title: str, message: str, status: str = "INFO") -> bool:
    """
    Sends a formatted JSON webhook alert to Slack, Discord, or custom endpoints.
    Supports: SUCCESS, WARNING, FAILURE, INFO statuses.
    """
    if not webhook_url:
        logger.warning("Webhook URL not provided. Skipping alert.")
        return False

    emoji = EMOJI_MAP.get(status, "🔔")
    color = COLOR_MAP.get(status, "#439FE0")

    payload = {
        "text": f"{emoji} *{title}*",
        "attachments": [
            {
                "color": color,
                "text": message
            }
        ]
    }

    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            if response.status in [200, 204]:
                logger.info(f"Alert sent successfully: [{status}] {title}")
                return True
            else:
                logger.warning(f"Webhook responded with unexpected status: {response.status}")
                return False

    except Exception as e:
        logger.error(f"Failed to dispatch webhook alert: {e}")
        return False


def alert_pipeline_success(webhook_url: str, batch_id: str, rows: int) -> bool:
    return send_webhook_alert(
        webhook_url,
        title="QDrift Pipeline — SUCCESS",
        message=f"Batch `{batch_id}` completed.\n{rows} rows processed successfully.",
        status="SUCCESS"
    )


def alert_drift_detected(webhook_url: str, drifted_cols: list, batch_id: str) -> bool:
    cols = ", ".join(drifted_cols)
    return send_webhook_alert(
        webhook_url,
        title="QDrift Pipeline — Drift Detected",
        message=f"Batch `{batch_id}`: Drift flagged in columns: `{cols}`",
        status="WARNING"
    )


def alert_pipeline_failure(webhook_url: str, error: str, batch_id: str) -> bool:
    return send_webhook_alert(
        webhook_url,
        title="QDrift Pipeline — FAILED",
        message=f"Batch `{batch_id}` failed.\nError: `{error}`",
        status="FAILURE"
    )