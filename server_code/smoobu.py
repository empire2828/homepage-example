import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets

@anvil.server.callable
def get_all_future_bookings():
    # Smoobu API endpoint für Reservierungen
    base_url = "https://login.smoobu.com/api/reservations"
    
    # API-Schlüssel aus Anvil Secrets holen
    api_key = anvil.secrets.get_secret('smoobu_api_key')
    
    # Headers mit API-Schlüssel für Autorisierung
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    # Parameter für die API-Anfrage
    params = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "confirmed",
        "page": 1,
        "limit": 100  # Maximale Anzahl von Buchungen pro Seite
    }
    
    all_bookings = []
    total_pages = 1
    current_page = 1
    
    # Alle Seiten durchlaufen
    while current_page <= total_pages:
        params["page"] = current_page
        
        # API-Anfrage senden
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Gesamtanzahl der Seiten aus der Antwort extrahieren (falls vorhanden)
            if "pagination" in data and "totalPages" in data["pagination"]:
                total_pages = data["pagination"]["totalPages"]
            
            # Buchungen aus der aktuellen Seite extrahieren
            if "data" in data:
                bookings = data["data"]
                all_bookings.extend(bookings)
            else:
                bookings = data
                all_bookings.extend(bookings)
            
            current_page += 1
        else:
            return f"Fehler: {response.status_code} - {response.text}"
    
    # Buchungen in die Anvil-Datenbank schreiben
    bookings_added = 0
    for booking in all_bookings:
        # Prüfen, ob die Buchung bereits in der Datenbank existiert
        existing = app_tables.bookings.get(reservation_id=booking['id'])
        
        if existing:
            # Aktualisiere bestehenden Eintrag
            existing.update(
                apartment=booking['apartment.Id'],
                arrival=booking['arrival'],
                departure=booking['departure'],
                guestname=booking['guest-name']          
            )
        else:
            # Neuen Eintrag hinzufügen
            app_tables.bookings.add_row(
                apartment=booking['apartment.Id'],
                arrival=booking['arrival'],
                departure=booking['departure'],
                guestname=booking['guest-name']          
            )
        
        bookings_added += 1
    
    return f"Erfolgreich {bookings_added} Buchungen abgerufen und in der Datenbank gespeichert."

# Funktion aufrufen, um zukünftige Buchungen zu holen und die Datenbank zu aktualisieren
result = get_all_future_bookings()
print(result)