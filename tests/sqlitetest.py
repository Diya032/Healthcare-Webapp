from sqlalchemy import create_engine, inspect
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# List all table names
tables = inspector.get_table_names()
print(tables)


from sqlalchemy import create_engine, inspect
from app.core.config import settings

# Connect to your database
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# List all tables and their columns
for table_name in inspector.get_table_names():
    print(f"Table: {table_name}")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
    print()
