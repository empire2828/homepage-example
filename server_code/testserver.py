import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.http

@anvil.server.callable
def resend_webhook(webhook_data):
    # URL Ihres Webhook-Endpunkts
    webhook_url = "https://guestscreener.com/_/smoobu/webhook"
    
    # Webhook-Daten senden
    response = anvil.http.request(
        webhook_url,
        method="POST",
        json=webhook_data,
        headers={"Content-Type": "application/json"}
    )
    
    return response

# Beispielaufruf mit Ihren Daten
webhook_data = {
    'action': 'updateRates', 
    'user': 585397, 
    'data': {
        '1646902': {
            '2026-02-06': {'price': 87, 'min_length_of_stay': 4, 'available': 0}, 
            '2026-02-07': {'price': 87, 'min_length_of_stay': 4, 'available': 0}
        }
    }
}

# Webhook erneut senden
result = resend_webhook(webhook_data)
print(f"Webhook erneut gesendet, Antwort: {result}")