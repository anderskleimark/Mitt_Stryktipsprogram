# Klass för att hantera flagg-ikoner.

class Country:

    _FLAGS = {
        "Sverige": "🇸🇪",
        "Norge": "🇳🇴",
        "Danmark": "🇩🇰",
        "Finland": "🇫🇮",
        "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "Skottland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
        "Wales": "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
        "Nordirland": "🇬🇧",
        "Irland": "🇮🇪",
        "Spanien": "🇪🇸",
        "Italien": "🇮🇹",
        "Frankrike": "🇫🇷",
        "Tyskland": "🇩🇪",
        "Nederländerna": "🇳🇱",
        "Belgien": "🇧🇪",
        "Portugal": "🇵🇹",
        "USA": "🇺🇸",
        "Österrike": "🇦🇹"
    }

    # Klassfunktion för att hämta ikonen för angivet land.
    @classmethod
    def get_flag(cls, country):
        return cls._FLAGS.get(country, "⚽")
