from sqlalchemy import create_engine, inspect
from app.core.database import SQLALCHEMY_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
inspector = inspect(engine)

columns = inspector.get_columns("slots")
print("slots table columns:")
for col in columns:
    print(f"- {col['name']} ({col['type']})")
