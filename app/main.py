"""FastAPI Application entrypoint, routers, static mounting, and lifespan management."""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.banking import router as banking_router
from app.api.v1.health import router as health_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.retail import router as retail_router
from app.api.middleware import RequestLoggingMiddleware
from app.config import settings
from app.database import init_db, SessionLocal
from app.etl.pipeline import ETLPipeline
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup migrations/init, then teardown."""
    logger.info("Initializing Data Ingestion & Analytics Platform...")
    try:
        init_db()
        logger.info("Database schemas and administrator accounts verified.")
    except Exception as exc:
        logger.error(f"Lifespan init_db warning: {exc}")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description="""
# Enterprise Data Ingestion & Analytics Platform
A modular, production-ready data engineering and analytics solution supporting:
* **Multi-Source Ingestion**: CSV, Microsoft Excel (.xlsx/.xls), JSON, and external REST APIs
* **Automated Data Quality & Validation**: Missing value detection, duplicate deduplication, phone/email format checks, numeric range validation, and dead-letter quarantine logging.
* **Transformations & Data Enrichment**: Date standardization, configurable currency exchange to USD, category mapping, revenue/tax/discount derivations, and customer spend tiers.
* **Relational Storage**: PostgreSQL / SQLite normalized 3NF schemas with SQLAlchemy ORM.
* **REST Analytics**: Top products, monthly sales velocity, VIP customers, revenue & gross margins, and banking income/expenses.
* **Power BI Connectivity**: Pre-engineered tabular models and DirectQuery endpoints.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging and security headers
app.add_middleware(RequestLoggingMiddleware)

# Mount Static Files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount Versioned API (/api/v1/...)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Root level shortcuts requested in project specification:
# POST /upload, GET /orders, GET /transactions, GET /customers, GET /products, GET /health, GET /analytics/...
app.include_router(health_router, tags=["Root Shortcuts"])
app.include_router(ingestion_router, tags=["Root Shortcuts"])
app.include_router(retail_router, tags=["Root Shortcuts"])
app.include_router(banking_router, tags=["Root Shortcuts"])
app.include_router(analytics_router, tags=["Root Shortcuts"])


@app.get("/", include_in_schema=False)
@app.get("/dashboard", include_in_schema=False)
async def serve_dashboard():
    """Serve the interactive HTML5 analytics dashboard."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        try:
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
        except Exception:
            return FileResponse(str(index_path))
    return JSONResponse({"message": f"{settings.APP_NAME} API running. Visit /docs for OpenAPI specifications."})


@app.post("/api/v1/seed-samples", tags=["Utilities"])
def seed_sample_data():
    """Ingest pre-packaged retail and banking sample datasets into the database."""
    base_dir = Path(__file__).parent.parent / "sample_data"
    pipeline = ETLPipeline()
    results = []

    # 1. Retail samples
    retail_csv = base_dir / "retail" / "customers.csv"
    if retail_csv.exists():
        r = pipeline.run(source=str(retail_csv), domain="retail", source_type="csv", source_name="sample_customers.csv")
        results.append(r)

    retail_sales = base_dir / "retail" / "retail_sales.csv"
    if retail_sales.exists():
        r = pipeline.run(source=str(retail_sales), domain="retail", source_type="csv", source_name="sample_retail_sales.csv")
        results.append(r)

    retail_dirty = base_dir / "retail" / "retail_dirty_batch.csv"
    if retail_dirty.exists():
        r = pipeline.run(source=str(retail_dirty), domain="retail", source_type="csv", source_name="retail_dirty_batch.csv")
        results.append(r)

    # 2. Banking samples
    banking_txns = base_dir / "banking" / "transactions.csv"
    if banking_txns.exists():
        r = pipeline.run(source=str(banking_txns), domain="banking", source_type="csv", source_name="sample_transactions.csv")
        results.append(r)

    banking_dirty = base_dir / "banking" / "banking_dirty_batch.csv"
    if banking_dirty.exists():
        r = pipeline.run(source=str(banking_dirty), domain="banking", source_type="csv", source_name="banking_dirty_batch.csv")
        results.append(r)

    return {"message": "Sample datasets processed successfully", "batches": results}


# Custom Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "detail": str(exc)},
    )
