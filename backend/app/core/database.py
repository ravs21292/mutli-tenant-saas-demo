"""
Database configuration and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for RLS policies
metadata = MetaData()


def get_db() -> Session:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def setup_rls_policies():
    """Setup Row Level Security policies for tenant isolation"""
    with engine.connect() as conn:
        # Enable RLS on all tenant-related tables
        rls_tables = [
            "users", "memberships", "projects", "files", "audit_logs"
        ]
        
        for table in rls_tables:
            try:
                # Enable RLS
                conn.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
                
                # Create policy for tenant isolation
                conn.execute(f"""
                    CREATE POLICY tenant_isolation ON {table}
                    FOR ALL
                    TO authenticated
                    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
                """)
                
                logger.info(f"RLS policy created for {table}")
            except Exception as e:
                logger.warning(f"RLS policy for {table} might already exist: {e}")
        
        conn.commit()
