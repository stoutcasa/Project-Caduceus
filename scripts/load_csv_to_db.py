import os
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path


# Load the generated CSV
csv_file = Path(__file__).resolve().parent.parent / "data" / "legacy_patient_data.csv"
print(f"Loading CSV from: {csv_file}")

df = pd.read_csv(csv_file, header=None, names=['full_name', 'dob_string', 'diagnosis_string', 'last_visit'])

# Add raw_id column (auto-increment starting from 1)
df.insert(0, 'raw_id', range(1, len(df) + 1))

print(f"Loaded {len(df)} rows from CSV")
print(df.head())


# Build source engine from env var SRC_DB_URL or fallback to default
def make_src_engine():
    url = os.getenv('SRC_DB_URL', 'mysql+mysqlconnector://root:rootpassword@127.0.0.1:3306/vista_dump')
    return create_engine(url, connect_args={'auth_plugin': 'mysql_native_password'})

src_engine = make_src_engine()

# Create table if it doesn't exist
try:
    with src_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS PATIENT_RAW (
                raw_id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(255),
                dob_string VARCHAR(20),
                diagnosis_string VARCHAR(255),
                last_visit DATE
            )
        """))
        conn.commit()
        print("Table PATIENT_RAW created (or already exists).")
except Exception as e:
    print("ERROR: could not connect to the source database.")
    print("Details:", e)
    print("If you can log in from the command line, set `SRC_DB_URL` environment variable, for example:")
    print("    set SRC_DB_URL=mysql+mysqlconnector://user:pass@host:3306/vista_dump")
    raise

# Load data into the table
df.to_sql('PATIENT_RAW', src_engine, if_exists='replace', index=False)
print(f"Successfully loaded {len(df)} rows into vista_dump.PATIENT_RAW")
