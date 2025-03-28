import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables
import requests
from datetime import datetime
import anvil.secrets

@anvil.server.callable
def my_server_function():
    # Function body
    return "Hello from the server!"
pass

@anvil.server.callable
def get_all_future_bookings():
    base_url = "https://login.smoobu.com/api/reservations"
    api_key = anvil.secrets.get_secret('smoobu_api_key')
    
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    params = {
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "status": "confirmed",
        "page": 1,
        "limit": 100
    }
    
    all_bookings = []
    total_pages = 1
    current_page = 1
    
    while current_page <= total_pages:
        params["page"] = current_page
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Correctly handle pagination
            if "pagination" in data and "totalPages" in data["pagination"]:
                total_pages = data["pagination"]["totalPages"]
            
            # Extract bookings from correct API response key
            if "bookings" in data:
                all_bookings.extend(data["bookings"])
            else:
                return "Error: Unexpected API response structure"
            
            current_page += 1
        else:
            return f"Fehler: {response.status_code} - {response.text}"
    
    bookings_added = 0
    for booking in all_bookings:
        try:
            # Get existing booking using reservation_id
            existing = app_tables.bookings.get(reservation_id=booking['id'])
            
            # Correct field access based on API documentation
            apartment_id = booking['apartment']['id']
            guest_name = booking['guest-name']
            
            if existing:
                existing.update(
                    apartment=apartment_id,
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=guest_name
                )
            else:
                app_tables.bookings.add_row(
                    reservation_id=booking['id'],
                    apartment=apartment_id,
                    arrival=booking['arrival'],
                    departure=booking['departure'],
                    guestname=guest_name
                )
            
            bookings_added += 1
        except KeyError as e:
            print(f"Missing key in booking data: {e}")
            continue
    
    return f"Erfolgreich {bookings_added} Buchungen abgerufen und gespeichert."

#result = get_all_future_bookings()()
#print 
