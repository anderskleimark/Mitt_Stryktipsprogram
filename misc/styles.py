class Style:
    BUTTON = {
        # Storlek
        "padding": "6px 12px",
        "margin": "0px",
        "font-size": "11pt",
        "min-height": "30px",
        "max-height": "120px",

    }
    DELETE_BUTTON = {
        **BUTTON,
        "background-color": "#C62828",
        "color": "white",

        "disabled-background-color": "#A0A0A0",
        "disabled-color": "#E0E0E0"
    }
