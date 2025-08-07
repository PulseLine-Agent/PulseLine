import asyncpg

from datetime import date

from twilio.twiml.voice_response import VoiceResponse

from Configs.config import USER, PASSWORD, DATABASE, HOST

from fastapi import Response

# This asynchronous function retrieves patient information from a PostgreSQL database
# using the patient's first and last name. It connects to the database with asyncpg,
# runs a parameterized SQL query to prevent SQL injection, fetches a single matching row,
# and formats the data into a readable sentence. If no match is found, it returns a default message.
async def get_patient_info(first_name: str, last_name: str):
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        host=HOST
    )
    row = await conn.fetchrow('SELECT * FROM public."Patient Information" WHERE "First Name" = $1 AND "Last Name" = $2', first_name, last_name)
    await conn.close()
    
    if row:
        return f"{row['First Name']} {row['Last Name']} was born on {row['Date of Birth']} and has a patient ID of {row['Patient ID']}. They are a {row['Gender']} with the phone number of {row['Phone Number']}. They live at {row['Address']} and their last visit date was {row['Last Visit Date']}. Their primary diagnosis is {row['Primary Diagnosis']} and they're allergic to {row['Allergies']} and take {row['Prescription']}. Their next visit date is {row['Next Visit Date']} and their doctor is {row['Doctor']}."
    else:
        return "No patient found with that name."

# Asynchronously updates the "Next Visit Date" for a patient in the database.
# Connects to a PostgreSQL database using asyncpg, validates the date format,
# performs an update query based on the patient's first and last name,
# and returns a status message indicating success or failure.
async def set_next_visit(first_name, last_name, next_visit: str) -> str:
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        host=HOST
    )
    
    try:
        next_visit_date = date.fromisoformat(next_visit)  # will raise ValueError if malformed
    except ValueError:
        return f"Error: next_visit '{next_visit}' is not a valid YYYY-MM-DD date."
    
    updated = await conn.execute(
        '''
        UPDATE public."Patient Information"
        SET "Next Visit Date" = $1
        WHERE "First Name" = $2 AND "Last Name" = $3
        ''',
        next_visit_date, first_name, last_name
    )
    await conn.close()

    if updated.endswith("UPDATE 1"):
        return f"Successfully set next visit for {first_name} {last_name} to {next_visit}."
    else:
        return f"No patient named {first_name} {last_name} found. No update performed."

# This asynchronous function attempts to refill a prescription for a patient.
# It connects to a PostgreSQL database using asyncpg, and searches for a patient
# in the "Patient Information" table using their first and last name.
# If a matching patient record is found, it returns a confirmation message that the prescription was refilled.
# Otherwise, it returns a message indicating no patient was found.
async def refill_prescription(first_name, last_name):
    conn = await asyncpg.connect(
        user=USER,
        password=PASSWORD,
        database=DATABASE,
        host=HOST
    )
    row = await conn.fetchrow('SELECT * FROM public."Patient Information" WHERE "First Name" = $1 AND "Last Name" = $2', first_name, last_name)
    await conn.close()
    
    if row:
        return f"Patient prescription of {row['Prescription']} refilled!."
    else:
        return "No patient found with that name."

# This asynchronous function handles redirecting a voice call.
# It creates a VoiceResponse (Twilio), plays a spoken message to the caller,
# adds a 60-second pause (simulating hold time), and then returns a confirmation string.
async def redirect_call():
    resp = VoiceResponse()
    
    resp.say("Please hold while I connect you to a specialist.")
    resp.pause(60)
    
    return "Redirecting call."