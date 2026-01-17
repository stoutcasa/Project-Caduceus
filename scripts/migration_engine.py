import os
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine


# Helper to build engine from env or fallback
def make_engine_from_env(env_var, fallback_url):
    url = os.getenv(env_var, fallback_url)
    return create_engine(url, connect_args={'auth_plugin': 'mysql_native_password'})


# 1. Connection Strings (can be overridden with env vars `SRC_DB_URL` and `TGT_DB_URL`)
# Example URL: mysql+mysqlconnector://user:pass@host:3306/database
src_engine = make_engine_from_env('SRC_DB_URL', 'mysql+mysqlconnector://root:rootpassword@127.0.0.1:3306/vista_dump')
tgt_engine = make_engine_from_env('TGT_DB_URL', 'mysql+mysqlconnector://root:rootpassword@127.0.0.1:3307/millennium_core')

print("--- Starting Migration ---")

# 2. Extract
df = pd.read_sql("SELECT * FROM PATIENT_RAW", src_engine)
print(f"Extracted {len(df)} rows.")

# 3. Transform: Split Names
def split_name(name_str):
    parts = name_str.split(',')
    if len(parts) >= 2:
        return parts[1].strip(), parts[0].strip() # First, Last
    return "Unknown", name_str

df[['FirstName', 'LastName']] = df['full_name'].apply(lambda x: pd.Series(split_name(x)))

# 4. Transform: Clean Dates (Simple logic for demo)
# Converts YYYYMMDD to YYYY-MM-DD
df['DOB_Clean'] = pd.to_datetime(df['dob_string'], errors='coerce')

# 5. Load Parent Table (PERSON)
person_df = df[['FirstName', 'LastName', 'DOB_Clean', 'raw_id']].copy()
person_df.rename(columns={'DOB_Clean': 'DOB', 'raw_id': 'LegacyID'}, inplace=True)

person_df.to_sql('PERSON', tgt_engine, if_exists='replace', index=False)
print("Loaded PERSON table.")

# 6. Transform & Load Child Table (CLINICAL_EVENT)
# Logic: We must iterate to split the diagnosis string 'E11, I10' into multiple rows
clinical_data = []

# Fetch the new PersonIDs to link them correctly
current_persons = pd.read_sql("SELECT PersonID, LegacyID FROM PERSON", tgt_engine)

for index, row in df.iterrows():
    diags = row['diagnosis_string'].split(',')
    for diag in diags:
        clinical_data.append({
            'LegacyID': row['raw_id'], 
            'DiagnosisCode': diag.strip(),
            'EventDate': row['last_visit']
        })

clinical_df = pd.DataFrame(clinical_data)

# Join with the new PERSON table to get the actual PersonID
final_clinical_df = pd.merge(clinical_df, current_persons, on='LegacyID')

final_clinical_df = final_clinical_df[['PersonID', 'DiagnosisCode', 'EventDate']]
final_clinical_df.to_sql('CLINICAL_EVENT', tgt_engine, if_exists='replace', index=False)

print(f"Loaded {len(final_clinical_df)} rows into CLINICAL_EVENT.")
print("--- Migration Complete ---")
