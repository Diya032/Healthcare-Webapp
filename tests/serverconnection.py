import pyodbc
import os

DATABASE_URL = os.getenv("DATABASE_URL")

conn = pyodbc.connect(
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=tcp:sqlhealthcareserver.database.windows.net,1433;"
    "Database=healthcare_sql_db;"
    "UID=healthcare_db_server;"
    "PWD=Health123;"
    "Encrypt=yes;TrustServerCertificate=no;"
)
cursor = conn.cursor()
cursor.execute("SELECT 1")
print(cursor.fetchone())
conn.close()
