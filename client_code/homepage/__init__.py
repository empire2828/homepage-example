from ._anvil_designer import homepageTemplate
from anvil import *
import anvil.server
#import anvil.google.auth
import anvil.users
#import anvil.tables as tables
#import anvil.tables.query as q
#from anvil.tables import app_tables

class homepage(homepageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run before the form opens.
    self.faq_repeating_panel.items = [
    {"question": "Was genau prüft die KI Suche?", "answer": "Die Suche sucht im Netz nach frei verfügbaren Informationen Ihrer Gäste und fasst diese zusammen. Gibt es mehrere Personen mit dem gleich oder ähnlichen Namen, kann die KI fehlerhafte Ergebnisse ausgeben."},
    {"question": "Was genau prüft die Adress- und Telefonprüfung?", "answer": "Die Adresse wird daraufhin geprüft, ob es diese überhaupt gibt. Es wird nicht geprüft, ob der Gast tatsächlich hier wohnt. Bei der Telefonnummer wird auf formale Richtigkeit geprüft, nicht ob der Gast diese konkrete Telefonnummer oder jemand Anderes diese hat."},
    {"question": "Wie erhält Guestscreener.com die Informationen über meine Gäste?", "answer": "Sie können Guestscreener.com per API direkt an Smoobu anbinden. Alternativ können Sie auch die Daten von einzelnen Gästen manuell eingeben."},
    {"question": "Wie bekommen Sie die Informationen zurück?", "answer": "Sobald eine neue Buchung in Smoobu erfasst wird, erhalten Sie automatisch eine eMail mit den Informationen. Alternativ können Sie alles im Dashboard hier sehen."},
    {"question": "Ist das Datenschutzkonform?", "answer": 
      "Guestscreener.com prüft Gästedaten für Ferienimmobilienvermieter auf Basis der DSGVO, da ein *berechtigtes Interesse* gemäß Art. 6 Abs. 1 lit. f DSGVO besteht: "
      "Der Vermieter darf personenbezogene Daten verarbeiten, wenn dies notwendig ist, um das Eigentum vor Schäden oder Betrug zu schützen – etwa durch eine Risikoprüfung potenzieller Gäste. "
      "Die Prüfung erfolgt ausschließlich anhand öffentlich zugänglicher Informationen, es werden keine sensiblen oder nicht relevanten Daten erhoben."
      "\n\n"
      "Die Datenverarbeitung ist auf das notwendige Maß beschränkt (Datenminimierung) und erfolgt nur für den klar definierten Zweck der Gefahrenabwehr (Zweckbindung). "
      "14 Tage nach Ablauf der Buchung werden die Daten automatisiert gelöscht."
      }
    ]

  def login_button_click(self, **event_args):
    user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=False, allow_remembered=True)
    if user:
      open_form('dashboard')
    pass

  def testen_button_click(self, **event_args):
    result = alert(
    content="Dieser Service richtet sich ausschließlich an Vermieter von Ferienimmobilien. Diese haben ein nach DSVGO legitimes Interesse daran, die Identität Ihre Gäste zu prüfen, um so ihr Eigentum zu schützen. Trifft das auf Sie zu?",
    title="Bestätigung berechtigtes Interesse nach DSVGO",
    large=True,
    buttons=[
        ("Yes", "YES"),
        ("No", "NO"),
    ]
    )
    if result=='YES':
      user = anvil.users.signup_with_form(allow_cancel=True)
      if user:
        anvil.server.call('send_registration_notification', user['email'])
        open_form('dashboard')
    pass

  def impressum_link_click(self, **event_args):
    open_form('impressum')
    pass

  def data_protection_link_click(self, **event_args):
    open_form('data_protection')
    pass

  def home_link_click(self, **event_args):
    open_form('homepage')
    pass

  def second_test_button_click(self, **event_args):
    self.testen_button_click()
    pass
