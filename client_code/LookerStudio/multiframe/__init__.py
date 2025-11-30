from ._anvil_designer import multiframeTemplate
from anvil import *
import anvil.server
from anvil.js.window import jQuery
from anvil.js import get_dom_node
import json
from ... import globals

class multiframe(multiframeTemplate):

  Locker_Version = "https://lookerstudio.google.com/embed/reporting/1eaf8e1d-9780-4e7c-9d4f-f0f392694afc/page/"

  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_user = globals.current_user
    self.supabase_key = ""

    if self.current_user is None:
      print("[multiframe] Warnung: Kein current_user verfügbar")
      return

    if self.current_user.get('smoobu_api_key') is None:
      self.pms_need_to_connect_text.visible = True
      self.channel_manager_connect_button.visible = True
    else:
      self.supabase_key = self.current_user.get('supabase_key', '')

      if self.supabase_key:
        self.content_panel.visible = True
        print(f"[multiframe] init {globals.current_user['email']} supabase key: {self.supabase_key}")
      else:
        print(f"{self.current_user['email']} Warnung: Kein supabase_key verfügbar")  

    self.iframe_urls = [
      f"{self.Locker_Version}qmCOF",            # Dashboard
      f"{self.Locker_Version}p_frni7wm2vd",     # Outlook
      f"{self.Locker_Version}p_8l5lnc13td",     # Profitability
      f"{self.Locker_Version}p_9euf3853td",     # Bookings
      f"{self.Locker_Version}p_knw9h153td",     # Cancellations
      f"{self.Locker_Version}p_1idplf63td",     # Occupancy
      f"{self.Locker_Version}p_8hyzd253td",     # Lead Time
      f"{self.Locker_Version}p_tilmy6zhtd",     # Guest Insights
      f"{self.Locker_Version}p_4dt5tycuud",     # Long Trends     
      f"{self.Locker_Version}p_cc0slxgtud",     # Detailed Bookings
      f"{self.Locker_Version}p_396qlut0wd",     # Knowledge hub
    ]

    self.panels = [
      self.looker_flow_panel_1,
      self.looker_flow_panel_2,
      self.looker_flow_panel_3,
      self.looker_flow_panel_4,
      self.looker_flow_panel_5,
      self.looker_flow_panel_6,
      self.looker_flow_panel_7,
      self.looker_flow_panel_8,
      self.looker_flow_panel_9,
      self.looker_flow_panel_10,
      self.looker_flow_panel_11,
    ]

    # Status-Tracking welche IFrames bereits geladen wurden
    self.geladene_iframes = [False] * len(self.iframe_urls)

    # Aktuell sichtbarer Index
    self.aktueller_index = None

    # Geräteerkennung
    self.ist_mobile = self._ist_mobile_geraet()

    if self.ist_mobile:
      print("[multiframe] 📱 MOBILE MODUS: Nur 1 iFrame gleichzeitig")
      self.max_cache_size = 1  # NUR aktuell sichtbares iFrame
    else:
      print("[multiframe] 🖥️ DESKTOP MODUS: Max 7 iFrames")
      self.max_cache_size = 7

    # Cache nur für Desktop
    self.iframe_cache = [] if not self.ist_mobile else None

    # Initial: alle Panels unsichtbar
    for i, panel in enumerate(self.panels):
      panel.visible = False
      panel.height = 2000

  def _ist_mobile_geraet(self):
    """Prüft ob Mobile-Gerät (aggressiver als nur Breite)"""
    try:
      breite = anvil.js.window.innerWidth

      # User Agent prüfen
      user_agent = anvil.js.window.navigator.userAgent.lower()
      ist_mobile_ua = any(x in user_agent for x in ['mobile', 'android', 'iphone', 'ipad'])

      # Touch-Support prüfen
      hat_touch = hasattr(anvil.js.window.navigator, 'maxTouchPoints') and \
      anvil.js.window.navigator.maxTouchPoints > 0

      # Kombinierte Prüfung
      ist_mobile = breite < 768 or ist_mobile_ua or hat_touch

      print(f"[multiframe] Gerät: Breite={breite}px, Mobile-UA={ist_mobile_ua}, Touch={hat_touch} → Mobile={ist_mobile}")
      return ist_mobile

    except Exception as e:
      print(f"[multiframe] Fehler bei Mobile-Erkennung: {e}")
      # Im Zweifel: Mobile-Modus (sicherer)
      return True

  def _entferne_alle_iframes_ausser(self, behalte_index):
    """AGGRESSIVE Methode: Entfernt ALLE iFrames außer dem angegebenen"""
    print(f"[multiframe] 🧹 Entferne alle iFrames außer {behalte_index}")

    for i in range(len(self.panels)):
      if i == behalte_index:
        continue  # Dieses behalten

      if self.geladene_iframes[i]:
        try:
          # Panel leeren
          jQuery(get_dom_node(self.panels[i])).empty()

          # Status zurücksetzen
          self.geladene_iframes[i] = False

          print(f"[multiframe]   ✓ iFrame {i} entfernt")
        except Exception as e:
          print(f"[multiframe]   ✗ Fehler bei iFrame {i}: {e}")

  def _entferne_aeltestes_iframe_desktop(self):
    """Desktop: Entfernt ältestes iFrame aus Cache"""
    if len(self.iframe_cache) == 0:
      return

    # Ältestes (außer aktuell sichtbares) entfernen
    for i in range(len(self.iframe_cache)):
      kandidat = self.iframe_cache[i]

      if kandidat == self.aktueller_index:
        continue

      self.iframe_cache.pop(i)

      try:
        panel = self.panels[kandidat]
        jQuery(get_dom_node(panel)).empty()
        self.geladene_iframes[kandidat] = False

        print(f"[multiframe] Desktop: iFrame {kandidat} entfernt (Cache: {self.iframe_cache})")
        return
      except Exception as e:
        print(f"[multiframe] Fehler beim Entfernen von iFrame {kandidat}: {e}")
        return

  def erstelle_iframe(self, index):
    """Erstellt ein IFrame für den gegebenen Index"""
    if index < 0 or index >= len(self.iframe_urls):        
      print(f"[multiframe] Ungültiger Index: {index}")
      return

    try:
      url = self.iframe_urls[index]
      panel = self.panels[index]

      # Parameter für Supabase Key
      if self.supabase_key:
        params = {"supabase_key_url": self.supabase_key}
        encoded_params = f"?params={anvil.js.window.encodeURIComponent(json.dumps(params))}"
        iframe_url = url + encoded_params
      else:
        iframe_url = url

      # Vorheriges entfernen
      jQuery(get_dom_node(panel)).empty()

      # Mobile: Kleinere Höhe für weniger Speicher
      hoehe = "1500" if self.ist_mobile else "1950"

      # IFrame erstellen
      iframe_attrs = {
        "src": iframe_url,
        "width": "100%",
        "height": hoehe,
        "frameborder": "0",
        "scrolling": "no",
        "loading": "eager" if self.ist_mobile else "lazy",  # Mobile: sofort laden
        "referrerpolicy": "origin-when-cross-origin",
        "allow": "storage-access"
      }

      iframe = jQuery("<iframe>").attr(iframe_attrs)
      iframe.appendTo(get_dom_node(panel))

      # Status setzen
      self.geladene_iframes[index] = True

      # Desktop: Cache aktualisieren
      if not self.ist_mobile:
        if index in self.iframe_cache:
          self.iframe_cache.remove(index)
        self.iframe_cache.append(index)

        while len(self.iframe_cache) > self.max_cache_size:
          self._entferne_aeltestes_iframe_desktop()

      print(f"[multiframe] ✓ iFrame {index} erstellt ({'Mobile' if self.ist_mobile else 'Desktop'})")

    except Exception as e:
      print(f"[multiframe] ✗ Fehler beim Erstellen von iFrame {index}: {e}")

  def lade_und_zeige_iframe(self, index):
    """Lädt IFrame falls nötig und zeigt es an"""
    if index < 0 or index >= len(self.iframe_urls):
      print(f"[multiframe] Ungültiger Index: {index}")
      return

    try:
      # Bereits sichtbar?
      if self.aktueller_index == index:
        print(f"[multiframe] iFrame {index} bereits sichtbar")
        return

      # 📱 MOBILE: ALLE anderen iFrames SOFORT entfernen
      if self.ist_mobile:
        print(f"[multiframe] 📱 Mobile: Wechsel zu iFrame {index}")

        # Verstecke vorheriges
        if self.aktueller_index is not None:
          self.panels[self.aktueller_index].visible = False

        # AGGRESSIVE Bereinigung: Entferne ALLE außer dem neuen
        self._entferne_alle_iframes_ausser(index)

        # Neues laden
        if not self.geladene_iframes[index]:
          print(f"[multiframe]   Lade iFrame {index}...")
          self.erstelle_iframe(index)

      # 🖥️ DESKTOP: Normales Cache-Management
      else:
        if self.aktueller_index is not None:
          self.panels[self.aktueller_index].visible = False

        if not self.geladene_iframes[index]:
          self.erstelle_iframe(index)

      # Anzeigen
      self.panels[index].visible = True
      self.aktueller_index = index

      print(f"[multiframe] ✓ iFrame {index} angezeigt")

      # Mobile: Garbage Collection triggern
      if self.ist_mobile:
        try:
          import gc
          gc.collect()
          print("[multiframe] 🗑️ Garbage Collection ausgeführt")
        except:
          pass

    except Exception as e:
      print(f"[multiframe] ✗ Fehler in lade_und_zeige_iframe({index}): {e}")
      import traceback
      traceback.print_exc()

  def verstecke_alle_iframes(self):
    """Versteckt alle IFrames"""
    try:
      for panel in self.panels:
        panel.visible = False
      self.aktueller_index = None

      # Mobile: Auch alle entladen
      if self.ist_mobile:
        self._entferne_alle_iframes_ausser(-1)  # Alle entfernen

    except Exception as e:
      print(f"[multiframe] Fehler beim Verstecken: {e}")

  def ist_geladen(self, index):
    """Prüft ob IFrame geladen ist"""
    if index < 0 or index >= len(self.geladene_iframes):
      return False
    return self.geladene_iframes[index]

  def channel_manager_connect_button_click(self, **event_args):
    open_form('channel_manager_connect')

  def dashboard_upgrade_button_click(self, **event_args):
    open_form('upgrade')

  def lade_restliche_iframes(self):
    """Hintergrund-Laden NUR auf Desktop"""
    if self.ist_mobile:
      print("[multiframe] 📱 Mobile: Hintergrund-Laden deaktiviert")
      return

    print("[multiframe] 🖥️ Desktop: Lade restliche iFrames...")
    for i in range(1, len(self.iframe_urls)):
      if not self.geladene_iframes[i]:
        try:
          self.erstelle_iframe(i)
        except Exception as e:
          print(f"[multiframe] Fehler bei Hintergrund-Laden von iFrame {i}: {e}")
