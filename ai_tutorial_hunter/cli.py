from __future__ import annotations
"""CLI entry point for AI Tutorial Hunter."""

import asyncio
import logging

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(name="tutorial-hunter", help="Discover trending AI tutorials")
console = Console()


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def run(
    max_trends: int = typer.Option(10, help="Max trends to detect"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Run the full discovery pipeline."""
    _setup_logging(log_level)

    from ai_tutorial_hunter.agents.orchestrator import Orchestrator

    async def _run():
        orch = Orchestrator()
        try:
            result = await orch.run(max_trends=max_trends)
        finally:
            await orch.close()
        return result

    result = asyncio.run(_run())

    # Display results
    if result.trends:
        console.print(f"\n[green]Trends detected:[/green] {len(result.trends)}")
        table = Table(title="Top Trends")
        table.add_column("Topic", style="green")
        table.add_column("Velocity", justify="right")
        table.add_column("Volume", justify="right")
        table.add_column("Sources")
        for t in result.trends[:10]:
            table.add_row(
                t.topic[:60], f"{t.velocity:.1f}", str(t.volume),
                ", ".join(t.sources),
            )
        console.print(table)

    if result.tutorials:
        console.print(f"\n[green]Tutorials ranked:[/green] {len(result.tutorials)}")
        table = Table(title="Top Tutorials")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Title", style="green")
        table.add_column("Source")
        table.add_column("Score", justify="right")
        table.add_column("Tier")
        for i, t in enumerate(result.tutorials[:15], 1):
            tier = result.tiers.get(t.id, "?")
            tier_style = "green" if str(tier) == "free" else "yellow"
            table.add_row(
                str(i), t.title[:55], t.source,
                f"{t.final_rank:.1f}",
                f"[{tier_style}]{tier}[/{tier_style}]",
            )
        console.print(table)

    if result.gaps:
        console.print(f"\n[yellow]Content gaps:[/yellow] {len(result.gaps)}")
        for gap in result.gaps[:5]:
            console.print(
                f"  • {gap.topic[:50]} — demand: {gap.demand_score:.0f}, "
                f"supply: {gap.supply_count}, gap: {gap.gap_score:.1f}"
            )


@app.command()
def detect_trends(
    limit: int = typer.Option(20, help="Max trends to return"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Detect currently trending AI topics."""
    _setup_logging(log_level)

    from ai_tutorial_hunter.agents.trend_detector import TrendDetector

    async def _run():
        detector = TrendDetector()
        try:
            return await detector.detect(limit=limit)
        finally:
            await detector.close()

    trends = asyncio.run(_run())
    table = Table(title=f"Trending AI Topics ({len(trends)} found)")
    table.add_column("Topic", style="green")
    table.add_column("Velocity", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Sources")
    for t in trends:
        table.add_row(
            t.topic[:60], f"{t.velocity:.1f}", str(t.volume),
            ", ".join(t.sources),
        )
    console.print(table)


@app.command()
def discover(
    topic: str = typer.Argument(help="Topic to search tutorials for"),
    limit: int = typer.Option(10, help="Max tutorials per source"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Discover tutorials for a specific topic."""
    _setup_logging(log_level)

    from ai_tutorial_hunter.agents.content_crawler import ContentCrawler
    from ai_tutorial_hunter.agents.quality_scorer import QualityScorer
    from ai_tutorial_hunter.models.trend import Trend

    async def _run():
        crawler = ContentCrawler()
        try:
            fake_trend = Trend(topic=topic, query=topic, velocity=50)
            tutorials = await crawler.crawl([fake_trend], max_per_trend=limit)
        finally:
            await crawler.close()
        scorer = QualityScorer()
        return scorer.score_all(tutorials)

    tutorials = asyncio.run(_run())
    table = Table(title=f"Tutorials for '{topic}' ({len(tutorials)} found)")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Title", style="green")
    table.add_column("Source")
    table.add_column("Type")
    table.add_column("Score", justify="right")
    for i, t in enumerate(tutorials[:20], 1):
        table.add_row(str(i), t.title[:55], t.source, t.content_type, f"{t.final_rank:.1f}")
    console.print(table)


@app.command()
def digest(
    format: str = typer.Option("console", help="Output format: console, html, email"),
    email_to: str = typer.Option("", help="Email recipient (for email format)"),
    log_level: str = typer.Option("INFO", help="Log level"),
) -> None:
    """Generate today's curated digest."""
    _setup_logging(log_level)

    from ai_tutorial_hunter.storage.database import Database
    from ai_tutorial_hunter.delivery.email_digest import generate_digest_html, send_digest

    db = Database()
    db.create_tables()
    tutorials = db.get_top_tutorials(limit=20)

    if not tutorials:
        console.print("[yellow]No tutorials in database. Run 'tutorial-hunter run' first.[/yellow]")
        return

    if format == "html":
        html = generate_digest_html(tutorials)
        console.print(html)
    elif format == "email" and email_to:
        html = generate_digest_html(tutorials)
        send_digest(email_to, html)
        console.print(f"[green]Digest sent to {email_to}[/green]")
    else:
        from ai_tutorial_hunter.models.monetization import classify_access
        table = Table(title="Today's Digest")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Title", style="green")
        table.add_column("Score", justify="right")
        table.add_column("Tier")
        for i, t in enumerate(tutorials[:15], 1):
            tier = classify_access(
                difficulty=t.difficulty,
                age_hours=t.age_hours,
                quality_score=t.quality_score,
                is_trending=t.trending_score > 30,
            ).value
            style = "green" if tier == "free" else "yellow"
            table.add_row(str(i), t.title[:55], f"{t.final_rank:.1f}", f"[{style}]{tier}[/{style}]")
        console.print(table)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to listen on"),
) -> None:
    """Start the API server."""
    import uvicorn
    from ai_tutorial_hunter.delivery.api_server import create_app

    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    app()
