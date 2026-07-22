from pathlib import Path

"""
Hanterar flaggbilder för länder.
"""


class Country:  # pylint: disable=too-few-public-methods
    """
    Klass för att hämta sökvägar till flaggbilder.
    """

    FLAG_CODES = {
        "Afghanistan": "af",
        "Albanien": "al",
        "Algeriet": "dz",
        "Andorra": "ad",
        "Angola": "ao",
        "Antigua och Barbuda": "ag",
        "Argentina": "ar",
        "Armenien": "am",
        "Australien": "au",
        "Azerbajdzjan": "az",

        "Belgien": "be",
        "Brasilien": "br",
        "Bulgarien": "bg",

        "Chile": "cl",
        "Colombia": "co",

        "Danmark": "dk",

        "England": "eng",

        "Finland": "fi",
        "Frankrike": "fr",

        "Ghana": "gh",
        "Grekland": "gr",

        "Indien": "in",
        "Irland": "ie",
        "Island": "is",
        "Italien": "it",

        "Japan": "jp",

        "Kanada": "ca",
        "Kina": "cn",
        "Kroatien": "hr",

        "Marocko": "ma",
        "Mexiko": "mx",

        "Nederländerna": "nl",
        "Norge": "no",
        "Nya Zeeland": "nz",

        "Polen": "pl",
        "Portugal": "pt",

        "Rumänien": "ro",
        "Ryssland": "ru",

        "Schweiz": "ch",
        "Serbien": "rs",
        "Skottland": "sct",
        "Spanien": "es",
        "Sverige": "se",
        "Sydafrika": "za",
        "Sydkorea": "kr",

        "Tjeckien": "cz",
        "Turkiet": "tr",
        "Tyskland": "de",

        "Ukraina": "ua",
        "Uruguay": "uy",
        "USA": "us",

        "Wales": "wls",

        "Österrike": "at",
    }

    @classmethod
    def get_flag_path(cls, country):
        """
        Returnerar sökvägen till landets flagga.
        Om landet saknas returneras unknown.png.
        """
        code = cls.FLAG_CODES.get(country)

        if code is None:
            return str(Path("resources") / "flags" / "unknown.png")

        return str(Path("resources") / "flags" / f"{code}.svg")
