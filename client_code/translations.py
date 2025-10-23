ORIGINAL_LOCALE = 'EN'
LOCALE = ''


TRANSLATIONS = {}


def set_dictionary(locale, dictionary):
  """Define a dictionary of translations for a given locale."""
  global TRANSLATIONS
  TRANSLATIONS[locale] = dictionary
  initialise(locale)

TRANSLATIONS_LOWER = {}
def initialise(locale=None):
  """Set the library up - construct a lower-case dictionary so we can fall back to case-insensitive comparisons."""
  for locale, dictionary in TRANSLATIONS.items():
    for original, translated in dictionary.items():
      if locale not in TRANSLATIONS_LOWER:
        TRANSLATIONS_LOWER[locale] = {}
      TRANSLATIONS_LOWER[locale][original.lower()] = translated.lower()
  if locale is not None:
    set_locale(locale)


def translate(original):
  """Translate a given string."""
  if LOCALE in TRANSLATIONS: 
    if original in TRANSLATIONS[LOCALE] or original.lower() in TRANSLATIONS_LOWER[LOCALE]:
      return TRANSLATIONS[LOCALE][original]
  return original


def _(original):
  """_ is a useful alias when you just want to wrap something in _() to translate it."""
  return translate(original)


TRANSLATION_REGISTER = {}
def register_translation(component, property_name):
  """Enable translations for a particular property on a component."""
  original_value = getattr(component, property_name)
  TRANSLATION_REGISTER.update({(component, property_name): original_value})
  setattr(component, property_name, translate(original_value))


def get_locale():
  return LOCALE


def set_locale(locale):
  """Set a new locale and re-run the translations for the registered objects."""
  global LOCALE
  LOCALE = locale
  apply_translations(locale)


def apply_translations(locale):
  """Apply the translations to all registered objects."""
  for (component, property_name), original in TRANSLATION_REGISTER.items():
    if LOCALE == ORIGINAL_LOCALE:
      setattr(component, property_name, original)
    else:
      setattr(component, property_name, translate(getattr(component, property_name)))


initialise()
