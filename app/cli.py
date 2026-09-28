"""Command-line interface (CLI) for executing the ETL pipeline and platform tasks with a single command."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.database import init_db, SessionLocal
from app.etl.pipeline import ETLPipeline
from app.services.analytics_service import AnalyticsService

app = typer.Typer(
    name="Chronicle CLI",
    help="Chronicle: Production Data Ingestion & Analytics Pipeline Command Line Interface",
    add_completion=False,
)
console = Console()


@app.command()
def init():
    """Initialize database schemas, create tables, and seed initial administrator."""
    console.print(Panel.fit("[bold green]Initializing Database Schemas & Tables...[/bold green]"))
    init_db()
    console.print("[bold green]✓[/bold green] Database initialization completed successfully.")


@app.command()
def run_pipeline(
    source: str = typer.Option(..., "--source", "-s", help="Path to input file (CSV, Excel, JSON) or REST API URL"),
    domain: str = typer.Option("retail", "--domain", "-d", help="Business domain: 'retail' or 'banking'"),
    source_type: str = typer.Option("csv", "--source-type", "-t", help="Source type: csv, excel, json, rest_api"),
    source_name: Optional[str] = typer.Option(None, "--name", "-n", help="Optional friendly source name"),
):
    """Execute the end-to-end ETL pipeline for a specific dataset with a single command."""
    console.print(
        Panel.fit(
            f"[bold cyan]Starting ETL Pipeline Execution[/bold cyan]\n"
            f"[yellow]Source:[/yellow] {source}\n"
            f"[yellow]Domain:[/yellow] {domain}\n"
            f"[yellow]Source Type:[/yellow] {source_type}"
        )
    )

    init_db()
    pipeline = ETLPipeline()
    result = pipeline.run(
        source=source,
        domain=domain,
        source_type=source_type,
        source_name=source_name or Path(source).name,
    )

    # Render pretty execution report
    status_color = "green" if result.get("status") == "completed" else "red"
    summary_table = Table(title="ETL Execution Summary", border_style="cyan")
    summary_table.add_column("Metric", style="bold white")
    summary_table.add_column("Value", style=status_color)

    summary_table.add_row("Batch ID", result.get("batch_id", "N/A"))
    summary_table.add_row("Status", result.get("status", "N/A").upper())
    summary_table.add_row("Total Records", str(result.get("total_records", 0)))
    summary_table.add_row("Valid Records Loaded", str(result.get("valid_records", 0)))
    summary_table.add_row("Quarantined Records", str(result.get("rejected_records", 0)))
    if "data_quality_pct" in result:
        summary_table.add_row("Data Quality Score", f"{result['data_quality_pct']}%")
    summary_table.add_row("Execution Duration", f"{result.get('execution_time_sec', 0)} seconds")

    console.print(summary_table)

    if result.get("rule_violations"):
        rules_table = Table(title="Validation Rule Failures", border_style="red")
        rules_table.add_column("Rule", style="yellow")
        rules_table.add_column("Violations Count", style="bold red")
        for rule, count in result["rule_violations"].items():
            rules_table.add_row(rule, str(count))
        console.print(rules_table)


@app.command()
def run_all_samples():
    """Execute end-to-end ingestion on all pre-packaged retail and banking sample datasets."""
    console.print(Panel.fit("[bold magenta]Ingesting All Retail & Banking Sample Datasets[/bold magenta]"))
    init_db()

    base_dir = Path(__file__).parent.parent / "sample_data"
    pipeline = ETLPipeline()

    tasks = [
        # Retail clean & dirty batches
        ("retail", "csv", str(base_dir / "retail" / "customers.csv"), "Customers Dimension (CSV)"),
        ("retail", "json", str(base_dir / "retail" / "products.json"), "Products Catalog (JSON)"),
        ("retail", "excel", str(base_dir / "retail" / "orders.xlsx"), "Orders & Items (Excel)"),
        ("retail", "csv", str(base_dir / "retail" / "retail_dirty_batch.csv"), "Dirty Retail Batch (CSV Quarantine Test)"),
        # Banking clean & dirty batches
        ("banking", "json", str(base_dir / "banking" / "accounts.json"), "Bank Accounts (JSON)"),
        ("banking", "csv", str(base_dir / "banking" / "transactions.csv"), "Bank Transactions (CSV)"),
        ("banking", "csv", str(base_dir / "banking" / "banking_dirty_batch.csv"), "Dirty Banking Batch (CSV Quarantine Test)"),
    ]

    for domain, stype, path_str, label in tasks:
        path_obj = Path(path_str)
        if not path_obj.exists():
            console.print(f"[yellow]Skipping {label} (file not generated yet at {path_str})[/yellow]")
            continue

        console.print(f"\n[cyan]▶ Processing:[/cyan] [bold]{label}[/bold]")
        res = pipeline.run(source=path_str, domain=domain, source_type=stype, source_name=path_obj.name)
        console.print(
            f"  [green]✓[/green] Batch {res['batch_id'][:8]} - "
            f"Loaded {res.get('valid_records', 0)}/{res.get('total_records', 0)} records "
            f"({res.get('rejected_records', 0)} quarantined) in {res.get('execution_time_sec', 0)}s"
        )

    console.print("\n[bold green]✓ All sample datasets processed successfully![/bold green]")


@app.command()
def show_analytics():
    """Print executive analytics summary directly in the terminal."""
    db = SessionLocal()
    try:
        rev = AnalyticsService.get_revenue_analytics(db)
        bank = AnalyticsService.get_banking_summary(db)
        dq = AnalyticsService.get_data_quality_metrics(db)

        # Revenue Panel
        console.print(
            Panel.fit(
                f"[bold green]Executive Retail Analytics[/bold green]\n"
                f"Total Revenue: [bold yellow]${rev.total_revenue:,.2f}[/bold yellow]\n"
                f"Total Orders: [bold cyan]{rev.total_orders:,}[/bold cyan]\n"
                f"Items Sold: [bold cyan]{rev.total_items_sold:,}[/bold cyan]\n"
                f"Average Order Value: [bold green]${rev.average_order_value:.2f}[/bold green]\n"
                f"Gross Profit Margin: [bold green]${rev.estimated_gross_profit:,.2f}[/bold green]"
            )
        )

        # Banking Panel
        console.print(
            Panel.fit(
                f"[bold blue]Banking & Cash Flow Telemetry[/bold blue]\n"
                f"Total Income: [bold green]${bank.total_income_usd:,.2f}[/bold green]\n"
                f"Total Expenses: [bold red]${bank.total_expenses_usd:,.2f}[/bold red]\n"
                f"Net Savings: [bold yellow]${bank.net_savings_usd:,.2f}[/bold yellow]\n"
                f"Savings Rate: [bold cyan]{bank.savings_rate_percentage:.1f}%[/bold cyan]\n"
                f"Total EMI Outflow: [bold magenta]${bank.total_emi_paid_usd:,.2f}[/bold magenta]"
            )
        )

        # Quality Panel
        console.print(
            Panel.fit(
                f"[bold magenta]Data Quality & Quarantine[/bold magenta]\n"
                f"Total Records Processed: {dq.total_records_processed:,}\n"
                f"Valid Records: [bold green]{dq.total_valid_records:,}[/bold green]\n"
                f"Quarantined Records: [bold red]{dq.total_rejected_records:,}[/bold red]\n"
                f"Overall Data Quality: [bold green]{dq.overall_quality_percentage:.1f}%[/bold green]"
            )
        )
    finally:
        db.close()


@app.command()
def start_server(
    host: str = typer.Option("0.0.0.0", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(False, "--reload", "-r"),
):
    """Start the FastAPI backend server with Uvicorn."""
    import uvicorn
    console.print(Panel.fit(f"[bold green]Starting Chronicle Server on http://{host}:{port}[/bold green]"))
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
