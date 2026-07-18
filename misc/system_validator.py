class SystemValidator:
    MATCH_COUNT = 13
    FULL = "1X2"  # Helgarderingar.
    HALF = {"1X", "12", "X2"}  # Halvgarderingar.
    FIXED = {"1", "X", "2"}  # Givna matcher.

    # Vilka U-tecken som är tillåtna för respektive ram.
    ALLOWED_KEY_VALUES = {
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
        self.full_allowed = 0
        self.half_allowed = 0
        self.fixed_allowed = self.MATCH_COUNT
        self.frame_values = [""] * self.MATCH_COUNT
        self.key_values = [""] * self.MATCH_COUNT
        self.math_values = [False] * self.MATCH_COUNT

    def set_system(self, system):
        self.full_allowed = system.full_covers
        self.half_allowed = system.half_covers

    # Funktion som ställer in ram-tecken för en viss match.
    def set_frame_value(self, match_number, value):
        self.frame_values[match_number - 1] = value

    # Funktion som uppdaterar ramtecknen för de tretton (13) matcherna.
    def update_frame_values(self, frame_values):
        self.frame_values = list(frame_values)

        while len(self.frame_values) < self.MATCH_COUNT:
            self.frame_values.append("")

    # Funktion som ställer i systemets U-rad.
    def set_key_value(self, match_number, value):
        self.key_values[match_number - 1] = value

    # Uppdaterar U-tecknen.
    def update_key_values(self, key_values):
        self.key_values = list(key_values)

        while len(self.key_values) < self.MATCH_COUNT:
            self.key_values.append("")

    # Funktion som säller in värdet på en matematisk gardering för en match.
    def set_mathematical_value(self, match_number, value):
        self.math_values[match_number - 1] = value

    # Funktion som uppdaterar de matematiska garderingarna för systemet.
    def update_mathematical_values(self, values):
        self.math_values = list(values)

    # Funktion som returnerar antalet helgarderingar.
    def get_full_count(self):
        return sum(
            value == self.FULL and not self.math_values[index]
            for index, value in enumerate(self.frame_values)
        )

    # Funktion som returnerar antal halvgarderingar.
    def get_half_count(self):
        return sum(
            value in self.HALF and not self.math_values[index]
            for index, value in enumerate(self.frame_values)
        )

    # Funktion som returnerar antal spikar.
    def get_fixed_count(self):
        return sum(
            value in self.FIXED
            for value in self.frame_values
        )

    # Funktion som returnerar antal tillåtna spikar.
    def get_fixed_allowed(self):
        return (
            self.MATCH_COUNT
            - self.full_allowed
            - self.half_allowed
            - sum(self.math_values)
        )

    # Funktion som returnerar statistik om systemet.
    def get_statistics(self):
        full = self.get_full_count()
        half = self.get_half_count()
        fixed = self.get_fixed_count()

        fixed_allowed = self.get_fixed_allowed()

        return {
            "full": full,
            "half": half,
            "fixed": fixed,
            "full_left": self.full_allowed - full,
            "half_left": self.half_allowed - half,
            "fixed_left": fixed_allowed - fixed
        }

    # Funktion som returnerar de ramtecken som är tillåtna för en viss match.
    def get_allowed_frame_values(self, row):
        frames = self.frame_values.copy()
        maths = self.math_values.copy()

        # Ta bort aktuell rad ur simuleringen
        if 0 <= row < self.MATCH_COUNT:
            frames[row] = ""
            maths[row] = False

        full = 0
        half = 0
        fixed = 0

        for i, value in enumerate(frames):

            if maths[i]:
                continue

            if value == self.FULL:
                full += 1

            elif value in self.HALF:
                half += 1

            elif value in self.FIXED:
                fixed += 1

        # Beräkna antal tillåtna spikar enligt samma regel som resten av klassen.
        fixed_allowed = (
            self.MATCH_COUNT
            - self.full_allowed
            - self.half_allowed
            - sum(maths)
        )

        allowed = [""]

        if fixed < fixed_allowed:
            allowed.extend([
                "1",
                "X",
                "2"
            ])

        if half < self.half_allowed:
            allowed.extend([
                "1X",
                "12",
                "X2"
            ])

        if full < self.full_allowed:
            allowed.append("1X2")

        current = self.frame_values[row]

        if current and current not in allowed:
            allowed.append(current)

        return allowed

    # Funktion som returnerar alla tillåtna U-tecken för en viss match.
    def get_allowed_key_values(self, row):
        frame = self.frame_values[row]

        allowed = list(
            self.ALLOWED_KEY_VALUES.get(frame, [""])
        )

        # Behåll nuvarande värde även om det inte längre är giltigt.
        current = self.key_values[row]

        if current and current not in allowed:
            allowed.append(current)

        return allowed

    # Funktion som kontrollerar om tipssystemets ram är giltigt.
    def validate_frame_vales(self):
        return (
            self.get_full_count() <= self.full_allowed
            and
            self.get_half_count() <= self.half_allowed
            and
            self.get_fixed_count() <= self.fixed_allowed
        )

    # Kontrollerar att alla U-tecken är giltiga.
    def validate_key_values(self):
        for frame, key in zip(
                self.frame_values,
                self.key_values):

            if key not in self.ALLOWED_VALUES.get(frame, [""]):
                return False

        return True
