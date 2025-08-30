from sqlalchemy import create_engine

connection_string = (
    "mssql+pyodbc://healthcare_db_server:Health123"
    "@sqlhealthcareserver.database.windows.net:1433/healthcare_sql_db"
    "?driver=ODBC+Driver+18+for+SQL+Server&encrypt=yes&TrustServerCertificate=no"
)

engine = create_engine(connection_string)
conn = engine.connect()
print("Connected:", conn)
