import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.email
from datetime import datetime, timedelta

@anvil.server.background_task
def send_new_signups():
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    
    users_table = anvil.users.get_user_table()
    
    # Neue Registrierungen
    new_users = [
        row for row in users_table.search()
        if row['signed_up'] is not None and row['signed_up'] >= last_24h
    ]
    emails = [row['email'] for row in new_users if row['email']]
    
    if emails:
        # Zusätzliche Statistiken
        total_enabled = len(users_table.search(enabled=True))
        active_subscriptions = len([
            row for row in users_table.search(enabled=True) 
            if row['subscription'] is not None
        ])
        
        # E-Mail-Text mit Statistiken
        email_body = f"""Neue User-Logins (letzte 24h):
        {", ".join(emails) or "Keine"}
        
        Gesamtstatistik:
        - Aktivierte User: {total_enabled}
        - Aktive Subscriptions: {active_subscriptions}"""
        
        anvil.email.send(
            to="dirk.klemer@gmail.com",
            subject="User-Report: Neue Logins & Statistiken",
            text=email_body
        )

@anvil.server.background_task
def delete_old_bookings():
    today = datetime.now().date()
    cutoff_date = today - timedelta(days=14)
    matching_rows = app_tables.bookings.search(departure=lambda d: d <= cutoff_date)
    deleted_count = 0
    for row in matching_rows:
        row.delete()
        deleted_count += 1
    print(f"Buchungen gelöscht, deren Abreisedatum 14 Tage oder mehr zurückliegt. Anzahl: {deleted_count}")
    return deleted_count
