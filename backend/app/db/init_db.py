from app.db.database import engine
from app.db.models import Base


def init_database():
    """
    Create all SupplyPrescript database tables.

    Requires PostgreSQL to be available through DATABASE_URL.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    print("Creating SupplyPrescript database tables...")
    init_database()
    print("Database tables created successfully.")