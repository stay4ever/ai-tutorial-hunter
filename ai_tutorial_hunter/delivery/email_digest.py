"""Email digest generator — creates and sends curated tutorial digests."""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template

from ai_tutorial_hunter.config.settings import get_settings
from ai_tutorial_hunter.models.tutorial import Tutorial
from ai_tutorial_hunter.models.monetization import AccessTier, classify_access

logger = logging.getLogger(__name__)

DIGEST_TEMPLATE = Template("""\
<!DOCTYPE html>
<html>
<head><style>
  body { font-family: monospace; background: #0a0a0a; color: #e0e0e0; padding: 20px; }
  h1 { color: #00ff41; }
  h2 { color: #00cc33; border-bottom: 1px solid #003300; padding-bottom: 8px; }
  .tutorial { background: #111; border: 1px solid #003300; border-radius: 8px; padding: 16px; margin: 12px 0; }
  .tutorial h3 { margin: 0 0 8px; }
  .tutorial h3 a { color: #00ff41; text-decoration: none; }
  .meta { color: #888; font-size: 0.85em; }
  .score { color: #00ff41; font-weight: bold; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; margin-right: 4px; }
  .free { background: #003300; color: #00ff41; }
  .premium { background: #332200; color: #ffaa00; }
  .beginner { background: #002233; color: #00aaff; }
  .footer { margin-top: 30px; color: #555; font-size: 0.8em; border-top: 1px solid #222; padding-top: 10px; }
</style></head>
<body>
  <h1>AI Tutorial Hunter — {{ digest_type }} Digest</h1>
  <p style="color: #888;">{{ date }} — {{ total }} tutorials discovered</p>

  <h2>Top Tutorials</h2>
  {% for t in tutorials %}
  <div class="tutorial">
    <h3><a href="{{ t.url }}">{{ t.title }}</a></h3>
    <p class="meta">
      {{ t.source }} · {{ t.author or "Unknown" }} · {{ t.content_type }}
      <span class="badge {{ t.tier }}">{{ t.tier }}</span>
      <span class="badge {{ t.difficulty }}">{{ t.difficulty }}</span>
    </p>
    <p>{{ t.summary[:200] }}{% if t.summary|length > 200 %}...{% endif %}</p>
    <p class="score">Score: {{ "%.1f"|format(t.final_rank) }}</p>
  </div>
  {% endfor %}

  {% if gaps %}
  <h2>Content Gaps — Topics Needing Tutorials</h2>
  <ul>
  {% for gap in gaps %}
    <li><strong>{{ gap.topic }}</strong> — demand: {{ "%.0f"|format(gap.demand_score) }}, only {{ gap.supply_count }} tutorials found</li>
  {% endfor %}
  </ul>
  {% endif %}

  <div class="footer">
    <p>AI Tutorial Hunter by nanoSYNAPSYS</p>
  </div>
</body>
</html>
""")


def generate_digest_html(
    tutorials: list[Tutorial],
    gaps: list | None = None,
    digest_type: str = "Daily",
) -> str:
    """Render the digest as HTML."""
    from datetime import datetime, timezone

    enriched = []
    for t in tutorials:
        tier = classify_access(
            difficulty=t.difficulty,
            age_hours=t.age_hours,
            quality_score=t.quality_score,
            is_trending=t.trending_score > 30,
        )
        enriched.append({
            **t.model_dump(),
            "tier": tier.value,
        })

    return DIGEST_TEMPLATE.render(
        tutorials=enriched,
        gaps=gaps or [],
        digest_type=digest_type,
        date=datetime.now(timezone.utc).strftime("%B %d, %Y"),
        total=len(tutorials),
    )


def send_digest(to: str, html: str, subject: str = "AI Tutorial Hunter — Daily Digest") -> bool:
    """Send digest email via SMTP."""
    settings = get_settings()
    if not settings.smtp_user or not settings.smtp_pass:
        logger.warning("SMTP not configured, skipping email send")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_user, to, msg.as_string())
        logger.info("Digest sent to %s", to)
        return True
    except Exception as e:
        logger.error("Failed to send digest: %s", e)
        return False
