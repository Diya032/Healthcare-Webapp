# import pyodbc
# import os

# DATABASE_URL = os.getenv("DATABASE_URL")

# conn = pyodbc.connect(
#     "Driver={ODBC Driver 18 for SQL Server};"
#     "Server=tcp:sqlhealthcareserver.database.windows.net,1433;"
#     "Database=healthcare_sql_db;"
#     "UID=healthcare_db_server;"
#     "PWD=Health123;"
#     "Encrypt=yes;TrustServerCertificate=no;"
# )
# cursor = conn.cursor()
# cursor.execute("SELECT 1")
# print(cursor.fetchone())
# conn.close()


import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy import text
from app.models.models import Doctor as doctors
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

DATABASE_URL = "mssql+pyodbc://healthcare_db_server:Health123@sqlhealthcareserver.database.windows.net:1433/healthcare_sql_db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

engine = sa.create_engine(DATABASE_URL)

# with engine.connect() as conn:
#     result = conn.execute(text("SELECT TOP 1 name FROM sys.tables"))
#     print(result.all())

#     result = conn.execute(text("SELECT name FROM sys.tables"))
#     print(result.all())

db: Session = SessionLocal()
inspector = inspect(engine)
# List columns for doctors table
# columns = inspector.get_columns("doctors")
doctors = db.query(doctors).all()
for d in doctors:
    print(d.id, d.name, d.specialty)
db.close()