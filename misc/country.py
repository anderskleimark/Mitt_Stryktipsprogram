from pathlib import Path

"""
Hanterar landsnamn och flagg-ikoner.
"""


def country_code_to_flag(code):
    """
    Omvandlar ISO 3166-1 alpha-2 kod till flagg-emoji.

    Exempel:
        SE -> 🇸🇪
    """
    return "".join(
        chr(ord(char) + 127397)
        for char in code.upper()
    )


class Country:  # pylint: disable=too-few-public-methods
    """
    Klass för att hämta flagg-ikoner för länder.
    """

    FLAG_FILES = {
        "Sverige": "se.svg",
        "Norge": "no.svg",
        "Danmark": "dk.svg",
        "Finland": "fi.svg",
        "Tyskland": "de.svg",
        "Spanien": "es.svg",
        "Frankrike": "fr.svg",
        "Italien": "it.svg",
        "England": "eng.svg",
        "Skottland": "sct.svg",
        "Wales": "wls.svg",
        "Schweiz": "ch.svg",
        "Irland": "ie.svg"
    }

    FLAGS = {
        "Afghanistan": country_code_to_flag("AF"),
        "Albanien": country_code_to_flag("AL"),
        "Algeriet": country_code_to_flag("DZ"),
        "Andorra": country_code_to_flag("AD"),
        "Angola": country_code_to_flag("AO"),
        "Antigua och Barbuda": country_code_to_flag("AG"),
        "Argentina": country_code_to_flag("AR"),
        "Armenien": country_code_to_flag("AM"),
        "Australien": country_code_to_flag("AU"),
        "Azerbajdzjan": country_code_to_flag("AZ"),

        "Belgien": country_code_to_flag("BE"),
        "Brasilien": country_code_to_flag("BR"),
        "Bulgarien": country_code_to_flag("BG"),

        "Chile": country_code_to_flag("CL"),
        "Colombia": country_code_to_flag("CO"),
        "Danmark": country_code_to_flag("DK"),

        "England": "🏴\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F",

        "Finland": country_code_to_flag("FI"),
        "Frankrike": country_code_to_flag("FR"),

        "Grekland": country_code_to_flag("GR"),
        "Ghana": country_code_to_flag("GH"),

        "Island": country_code_to_flag("IS"),
        "Indien": country_code_to_flag("IN"),
        "Irland": country_code_to_flag("IE"),
        "Italien": country_code_to_flag("IT"),

        "Japan": country_code_to_flag("JP"),

        "Kanada": country_code_to_flag("CA"),
        "Kina": country_code_to_flag("CN"),
        "Kroatien": country_code_to_flag("HR"),

        "Marocko": country_code_to_flag("MA"),
        "Mexiko": country_code_to_flag("MX"),

        "Nederländerna": country_code_to_flag("NL"),
        "Norge": country_code_to_flag("NO"),
        "Nya Zeeland": country_code_to_flag("NZ"),

        "Polen": country_code_to_flag("PL"),
        "Portugal": country_code_to_flag("PT"),

        "Rumänien": country_code_to_flag("RO"),
        "Ryssland": country_code_to_flag("RU"),

        "Schweiz": country_code_to_flag("CH"),
        "Serbien": country_code_to_flag("RS"),
        "Skottland": "🏴\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F",
        "Spanien": country_code_to_flag("ES"),
        "Sverige": country_code_to_flag("SE"),
        "Sydafrika": country_code_to_flag("ZA"),
        "Sydkorea": country_code_to_flag("KR"),

        "Tjeckien": country_code_to_flag("CZ"),
        "Turkiet": country_code_to_flag("TR"),
        "Tyskland": country_code_to_flag("DE"),

        "Ukraina": country_code_to_flag("UA"),
        "Uruguay": country_code_to_flag("UY"),
        "USA": country_code_to_flag("US"),

        "Wales": "🏴\U000E0067\U000E0062\U000E0077\U000E006C\U000E0073\U000E007F",

        "Österrike": country_code_to_flag("AT"),
    }

    @classmethod
    def get_flag(cls, country):
        """
        Returnerar flagg-emoji för ett land.

        Om landet saknas returneras en fotbolls-emoji.
        """
        return cls.FLAGS.get(country, "⚽")

    @classmethod
    def get_flag_path(cls, country):
        """
        Returnerar sökväg till flagga.
        """
        filename = cls.FLAG_FILES.get(country)

        if filename is None:
            return ""

        return f"resources/flags/{filename}"
