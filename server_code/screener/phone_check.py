import anvil.facebook.auth
import anvil.server
import phonenumbers
#from phonenumbers import  timezone
#from phonenumbers import  geocoder, carrier

@anvil.server.callable
def phone_check(phone_number, default_region="DE"):
    """
    Validiert eine Telefonnummer mit der Google libphonenumber Bibliothek
    
    Args:
        phone_number (str): Die zu validierende Telefonnummer
        default_region (str, optional): Der Standardländercode (z.B. 'DE' für Deutschland)
        
    Returns:
        bool: True wenn die Nummer gültig ist, sonst False
    """
    try:
        # Wenn keine Telefonnummer angegeben wurde
        if not phone_number:
            return False
        
        # Parsen der Telefonnummer
        parsed_number = phonenumbers.parse(phone_number, default_region)
        
        # Überprüfen, ob die Nummer gültig ist und das Ergebnis zurückgeben
        return phonenumbers.is_valid_number(parsed_number)
        
    except phonenumbers.NumberParseException:
        # Bei Parsing-Fehlern ist die Nummer ungültig
        return False
    except Exception:
        # Bei anderen Fehlern ebenfalls False zurückgeben
        return False


def get_number_type_name(number_type):
    types = {
        phonenumbers.PhoneNumberType.FIXED_LINE: "Festnetz",
        phonenumbers.PhoneNumberType.MOBILE: "Mobiltelefon",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Festnetz oder Mobiltelefon",
        phonenumbers.PhoneNumberType.TOLL_FREE: "Gebührenfrei",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium-Rate",
        phonenumbers.PhoneNumberType.SHARED_COST: "Geteilte Kosten",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Persönliche Nummer",
        phonenumbers.PhoneNumberType.PAGER: "Pager",
        phonenumbers.PhoneNumberType.UAN: "UAN",
        phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unbekannt"
    }
    return types.get(number_type, "Unbekannt")

