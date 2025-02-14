import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Function to upsert train entries in Supabase
def upsert_train_entry(train, table_name):
    today = datetime.date.today().isoformat()

    # Check if the train already exists for today
    response = supabase.table(table_name).select("*") \
        .eq("train_number", train['train_number']) \
        .eq("date", today) \
        .execute()

    track_var = train['track'] if train['track'] else None
    print(f"Track var is-{track_var}")

    if response.data:
        # If the train exists, update the existing record
        supabase.table(table_name).update({
            "time": train['time'],
            "train_name": train['train_name'],
            "destination": train['destination'],
            "status": train['status'],
            "track": track_var
        }).eq("train_number", train['train_number']).eq("date", today).execute()
    else:
        # Insert a new train entry
        supabase.table(table_name).insert({
            "time": train['time'],
            "train_number": train['train_number'],
            "train_name": train['train_name'],
            "destination": train['destination'],
            "status": train['status'],
            "track": track_var,
            "date": today
        }).execute()


