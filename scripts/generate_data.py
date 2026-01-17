import pandas as pd
import random
from faker import Faker
from pathlib import Path

fake = Faker()
NUM_ROWS = 2000
# Use an absolute path relative to the repository root (two levels up from this script)
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "legacy_patient_data.csv"
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

def messy_dob():
    """Generates inconsistent dates (YYYYMMDD or YYYY-MM-DD)"""
    if random.random() < 0.8:
        return fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y%m%d')
    return fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d')

def messy_diagnosis():
    """Generates comma-separated codes (Anti-pattern)"""
    codes = ['E11.9', 'I10', 'Z00.0', 'J45.9', 'M54.5']
    return ",".join(random.sample(codes, random.randint(1, 3)))

data = []
for _ in range(NUM_ROWS):
    # Format: LASTNAME, FIRSTNAME (Common in mainframes)
    full_name = f"{fake.last_name().upper()}, {fake.first_name().upper()}"
    
    data.append({
        "full_name": full_name,
        "dob_string": messy_dob(),
        "diagnosis_string": messy_diagnosis(),
        "last_visit": fake.date_this_decade().strftime('%Y-%m-%d')
    })

df = pd.DataFrame(data)
# Write without header for easier MySQL import
df.to_csv(OUTPUT_FILE, index=False, header=False) 
print(f"Generated {NUM_ROWS} rows to {OUTPUT_FILE}")
