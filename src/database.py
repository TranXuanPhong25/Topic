"""Database setup and session management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from models import Base
from configs.config import DATABASE_URL


# Create engine
# For SQLite, we use check_same_thread=False to allow multi-threading
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def drop_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped!")


def get_db() -> Generator[Session, None, None]:
    """
    Get database session for dependency injection in FastAPI.
    
    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Get database session as context manager.
    
    Usage:
        with get_db_context() as db:
            db.add(item)
            db.commit()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """
    Database manager for easy CRUD operations.
    Useful for simple scripts and testing.
    """
    
    def __init__(self):
        self.SessionLocal = SessionLocal
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_tables(self):
        """Create all tables"""
        create_tables()
    
    def drop_tables(self):
        """Drop all tables"""
        drop_tables()
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around operations.
        Automatically commits or rolls back.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()


def init_database():
    """Initialize database with tables and default data"""
    print("Initializing database...")
    create_tables()
    
    # Add default clinic settings (optional)
    with get_db_context() as db:
        from models import ClinicSettings
        
        # Check if settings already exist
        existing = db.query(ClinicSettings).first()
        if not existing:
            # Add default settings
            settings = [
                ClinicSettings(
                    key="appointment_duration",
                    value="30",
                    description="Default appointment duration in minutes"
                ),
                ClinicSettings(
                    key="max_daily_appointments",
                    value="20",
                    description="Maximum appointments per day"
                ),
                ClinicSettings(
                    key="business_hours_start",
                    value="09:00",
                    description="Clinic opening time"
                ),
                ClinicSettings(
                    key="business_hours_end",
                    value="17:00",
                    description="Clinic closing time"
                ),
            ]
            
            for setting in settings:
                db.add(setting)
            
            db.commit()
            print("✅ Default clinic settings added!")
    
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
