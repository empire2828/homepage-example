from ._anvil_designer import homepageTemplate
from anvil import *
import anvil.server
import anvil.users

class homepage(homepageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.faq_repeating_panel.items = [
    {"question": "Was genau prüft die KI Suche?", "answer": "Die Suche sucht im Netz nach frei verfügbaren Informationen Ihrer Gäste und fasst diese zusammen. Gibt es mehrere Personen mit dem gleich oder ähnlichen Namen, kann die KI fehlerhafte Ergebnisse ausgeben."},
    {"question": "Was genau prüft die Adress- und Telefonprüfung?", "answer": "Die Adresse wird daraufhin geprüft, ob es diese überhaupt gibt. Es wird nicht geprüft, ob der Gast tatsächlich hier wohnt. Bei der Telefonnummer wird auf formale Richtigkeit geprüft, nicht ob der Gast diese konkrete Telefonnummer oder jemand Anderes diese hat."},
    {"question": "Wie erhält Lodginia.com die Informationen über meine Gäste?", "answer": "Sie können Lodginia.com per API direkt an Smoobu anbinden. Alternativ können Sie auch die Daten von einzelnen Gästen manuell eingeben."},
    {"question": "Wie bekommen Sie die Informationen zurück?", "answer": "Sobald eine neue Buchung in Smoobu erfasst wird, erhalten Sie automatisch eine eMail mit den Informationen. Alternativ können Sie alles im Dashboard hier sehen."},
    {"question": "Ist das Datenschutzkonform?", "answer": 
      "Lodginia.com prüft Gästedaten für Ferienimmobilienvermieter auf Basis der DSGVO, da ein *berechtigtes Interesse* gemäß Art. 6 Abs. 1 lit. f DSGVO besteht: "
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
      # Layout Template öffnen
      layout_form = open_form('layout_template')
      multiframe_form_preload= open_form('LookerStudio.multiframe')
  
      # Dashboard automatisch laden
      multiframe_form = multiframe_form_preload.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
  
      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
    pass

  def testen_button_click(self, **event_args):
    user = anvil.users.signup_with_form(allow_cancel=True)
    if user:
      anvil.server.call('create_supabase_key')
      anvil.server.call('send_registration_notification', user['email'])
      # Layout Template öffnen
      layout_form = open_form('layout_template')
      # Dashboard automatisch laden
      multiframe_form = layout_form.open_multiframe_form()
      multiframe_form.lade_und_zeige_iframe(0)  # Index 0 = Dashboard
      # Navigation Link als aktiv markieren
      layout_form.reset_links()
      layout_form.dashboard_navigation_link.selected = True
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

