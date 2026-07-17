class SystemKeyValidator:

    MATCH_COUNT = 13

    # Vilka U-tecken som är tillåtna för respektive ram.
    ALLOWED_VALUES = {
        "": [""],
        "1": [""],
        "X": [""],
        "2": [""],
        "1X": ["", "1", "X"],
        "12": ["", "1", "2"],
        "X2": ["", "X", "2"],
        "1X2": ["", "1", "X", "2"],
    }

    def __init__(self):

        self.frame_values = [""] * self.MATCH_COUNT
        self.key_values = [""] * self.MATCH_COUNT

    # Uppdaterar ramarna.
    def update_frames(self, frame_values):
        self.frame_values = list(frame_values)

        while len(self.frame_values) < self.MATCH_COUNT:
            self.frame_values.append("")

    # Uppdaterar U-tecknen.
    def update_keys(self, key_values):

        self.key_values = list(key_values)

        while len(self.key_values) < self.MATCH_COUNT:
            self.key_values.append("")

    # Returnerar tillåtna U-tecken för en viss match.
    def get_allowed_values(self, row):

        frame = self.frame_values[row]

        allowed = list(
            self.ALLOWED_VALUES.get(frame, [""])
        )

        # Behåll nuvarande värde även om det inte längre är giltigt.
        current = self.key_values[row]

        if current and current not in allowed:
            allowed.append(current)

        return allowed

    # Kontrollerar att alla U-tecken är giltiga.
    def validate(self):

        for frame, key in zip(
                self.frame_values,
                self.key_values):

            if key not in self.ALLOWED_VALUES.get(frame, [""]):
                return False

        return True
