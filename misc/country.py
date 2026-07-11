# Klass för att hantera flagg-ikoner.

class Country:

    _FLAGS = {
        "Sverige": "🇸🇪",
        "Norge": "🇳🇴",
        "Danmark": "🇩🇰",
        "Finland": "🇫🇮",
        "England": "🏴",
        "Skottland": "🏴",
        "Wales": "🏴",
        "Nordirland": "🇬🇧",
        "Spanien": "🇪🇸",
        "Italien": "🇮🇹",
        "Frankrike": "🇫🇷",
        "Tyskland": "🇩🇪",
        "Nederländerna": "🇳🇱",
        "Belgien": "🇧🇪",
        "Portugal": "🇵🇹",
        "USA": "🇺🇸"
    }

    # Klassfunktion för att hämta ikonen för angivet land.
    @classmethod
    def get_flag(cls, country):
        return cls._FLAGS.get(country, "⚽")
