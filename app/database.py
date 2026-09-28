"""Database connection, engine, session factory, and initialization."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings
from app.utils.logger import logger

# Configure database engine arguments
connect_args = {}
engine_kwargs = {
    "echo": settings.DB_ECHO,
}

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine_kwargs["connect_args"] = connect_args
else:
    # PostgreSQL settings
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields an active database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables and seed initial administrator account if needed."""
    from app.models import (
        User,
        IngestionBatch,
        RejectedRecord,
        AuditLog,
        Location,
        Category,
        Customer,
        Product,
        Order,
        OrderItem,
        BankAccount,
        Merchant,
        Transaction,
    )
    from app.utils.security import get_password_hash

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")

    # Seed Admin User if not existing
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == settings.INITIAL_ADMIN_EMAIL).first()
        if not existing_admin:
            admin_user = User(
                email=settings.INITIAL_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.INITIAL_ADMIN_PASSWORD),
                full_name=settings.INITIAL_ADMIN_NAME,
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info("Initial administrator account created", email=settings.INITIAL_ADMIN_EMAIL)
    except Exception as exc:
        db.rollback()
        logger.error(f"Error seeding initial admin: {exc}")
    finally:
        db.close()
