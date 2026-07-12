# Klass för att hantera flagg-ikoner.

class Country:

    def country_code_to_flag(code):
        """
        Omvandlar ISO 3166-1 alpha-2 kod till flagg-emoji.
        Exempel: SE -> 🇸🇪
        """
        return "".join(
            chr(ord(char) + 127397)
            for char in code.upper()
        )

    _FLAGS = {
        "Afghanistan": country_code_to_flag("AF"),
        "Albanien": country_code_to_flag("AL"),
        "Algeriet": country_code_to_flag("DZ"),
        "Andorra": country_code_to_flag("AD"),
        "Angola": country_code_to_flag("AO"),
        "Antigua och Barbuda": country_code_to_flag("AG"),
        "Argentina": country_code_to_flag("AR"),
        "Armenien": country_code_to_flag("AM"),
        "Australien": country_code_to_flag("AU"),
        "Österrike": country_code_to_flag("AT"),
        "Azerbajdzjan": country_code_to_flag("AZ"),

        "Bahamas": country_code_to_flag("BS"),
        "Bahrain": country_code_to_flag("BH"),
        "Bangladesh": country_code_to_flag("BD"),
        "Barbados": country_code_to_flag("BB"),
        "Belgien": country_code_to_flag("BE"),
        "Belize": country_code_to_flag("BZ"),
        "Benin": country_code_to_flag("BJ"),
        "Bhutan": country_code_to_flag("BT"),
        "Bolivia": country_code_to_flag("BO"),
        "Bosnien och Hercegovina": country_code_to_flag("BA"),
        "Brasilien": country_code_to_flag("BR"),
        "Bulgarien": country_code_to_flag("BG"),

        "Chile": country_code_to_flag("CL"),
        "Colombia": country_code_to_flag("CO"),
        "Costa Rica": country_code_to_flag("CR"),
        "Cypern": country_code_to_flag("CY"),
        "Danmark": country_code_to_flag("DK"),
        "Dominikanska republiken": country_code_to_flag("DO"),

        "Ecuador": country_code_to_flag("EC"),
        "Egypten": country_code_to_flag("EG"),
        "El Salvador": country_code_to_flag("SV"),
        "England": "🏴\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F",
        "Estland": country_code_to_flag("EE"),
        "Etiopien": country_code_to_flag("ET"),

        "Finland": country_code_to_flag("FI"),
        "Frankrike": country_code_to_flag("FR"),
        "Förenade Arabemiraten": country_code_to_flag("AE"),
        "Förenade kungariket": country_code_to_flag("GB"),

        "Georgien": country_code_to_flag("GE"),
        "Ghana": country_code_to_flag("GH"),
        "Grekland": country_code_to_flag("GR"),
        "Guatemala": country_code_to_flag("GT"),

        "Haiti": country_code_to_flag("HT"),
        "Honduras": country_code_to_flag("HN"),
        "Hongkong": country_code_to_flag("HK"),
        "Ungern": country_code_to_flag("HU"),

        "Island": country_code_to_flag("IS"),
        "Indien": country_code_to_flag("IN"),
        "Indonesien": country_code_to_flag("ID"),
        "Iran": country_code_to_flag("IR"),
        "Irak": country_code_to_flag("IQ"),
        "Irland": country_code_to_flag("IE"),
        "Israel": country_code_to_flag("IL"),
        "Italien": country_code_to_flag("IT"),

        "Japan": country_code_to_flag("JP"),
        "Jordanien": country_code_to_flag("JO"),

        "Kanada": country_code_to_flag("CA"),
        "Kina": country_code_to_flag("CN"),
        "Kroatien": country_code_to_flag("HR"),
        "Kuba": country_code_to_flag("CU"),
        "Kuwait": country_code_to_flag("KW"),

        "Lettland": country_code_to_flag("LV"),
        "Libanon": country_code_to_flag("LB"),
        "Litauen": country_code_to_flag("LT"),
        "Luxemburg": country_code_to_flag("LU"),

        "Malaysia": country_code_to_flag("MY"),
        "Malta": country_code_to_flag("MT"),
        "Marocko": country_code_to_flag("MA"),
        "Mexiko": country_code_to_flag("MX"),
        "Moldavien": country_code_to_flag("MD"),
        "Monaco": country_code_to_flag("MC"),

        "Nederländerna": country_code_to_flag("NL"),
        "Nya Zeeland": country_code_to_flag("NZ"),
        "Nicaragua": country_code_to_flag("NI"),
        "Nigeria": country_code_to_flag("NG"),
        "Nordirland": "🇬🇧",
        "Norge": country_code_to_flag("NO"),

        "Pakistan": country_code_to_flag("PK"),
        "Panama": country_code_to_flag("PA"),
        "Peru": country_code_to_flag("PE"),
        "Polen": country_code_to_flag("PL"),
        "Portugal": country_code_to_flag("PT"),

        "Qatar": country_code_to_flag("QA"),

        "Rumänien": country_code_to_flag("RO"),
        "Ryssland": country_code_to_flag("RU"),

        "Saudiarabien": country_code_to_flag("SA"),
        "Schweiz": country_code_to_flag("CH"),
        "Serbien": country_code_to_flag("RS"),
        "Singapore": country_code_to_flag("SG"),
        "Slovakien": country_code_to_flag("SK"),
        "Slovenien": country_code_to_flag("SI"),
        "Spanien": country_code_to_flag("ES"),
        "Sydafrika": country_code_to_flag("ZA"),
        "Sydkorea": country_code_to_flag("KR"),
        "Sverige": country_code_to_flag("SE"),
        "Skottland": "🏴\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F",

        "Thailand": country_code_to_flag("TH"),
        "Tjeckien": country_code_to_flag("CZ"),
        "Turkiet": country_code_to_flag("TR"),
        "Tyskland": country_code_to_flag("DE"),

        "Ukraina": country_code_to_flag("UA"),
        "Uruguay": country_code_to_flag("UY"),
        "USA": country_code_to_flag("US"),

        "Venezuela": country_code_to_flag("VE"),
        "Vietnam": country_code_to_flag("VN"),

        "Wales": "🏴\U000E0067\U000E0062\U000E0077\U000E0061\U000E006C\U000E007F",

        "Österrike": country_code_to_flag("AT")
    }

    # Klassfunktion för att hämta ikonen för angivet land.
    @classmethod
    def get_flag(cls, country):
        return cls._FLAGS.get(country, "⚽")
