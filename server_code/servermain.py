import anvil.email
import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

class Guest:
    def __init__(self, first_name, last_name, street, house_number, postal_code, city):
        self.first_name = first_name
        self.last_name = last_name
        self.street = street
        self.house_number = house_number
        self.postal_code = postal_code
        self.city = city
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_address(self):
        return f"{self.street} {self.house_number}, {self.postal_code} {self.city}"
    
    def __str__(self):
        return f"{self.get_full_name()}, {self.get_full_address()}"
    
    def update_address(self, street=None, house_number=None, postal_code=None, city=None):
        if street:
            self.street = street
        if house_number:
            self.house_number = house_number
        if postal_code:
            self.postal_code = postal_code
        if city:
            self.city = city
