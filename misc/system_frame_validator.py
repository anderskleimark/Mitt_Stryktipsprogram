# Klass för att validera ramen för tipssystem.

class SystemFrameValidator:

    MATCH_COUNT = 13
    FULL = "1X2"  # Helgarderingar.
    HALF = {"1X", "12", "X2"}  # Halvgarderingar.
    FIXED = {"1", "X", "2"}  # Givna matcher.

    def __init__(self):
        self.full_allowed = 0
        self.half_allowed = 0
        self.fixed_allowed = self.MATCH_COUNT
        self.frame_values = [""] * self.MATCH_COUNT
        self.math_values = [False] * self.MATCH_COUNT

    # Funktion som ställer in vilket tipssystem som används.
    def set_system(self, system):

        self.full_allowed = system.full_covers
        self.half_allowed = system.half_covers

    # Funktion som uppdaterar ramtecknen för de tretton (13) matcherna.
    def update_frames(self, frame_values):
        self.frame_values = list(frame_values)

        while len(self.frame_values) < self.MATCH_COUNT:
            self.frame_values.append("")

    # Funktion som returnerar antalet helgarderingar.
    def get_full_count(self):
        return sum(
            value == self.FULL and not self.math_values[index]
            for index, value in enumerate(self.frame_values)
        )

    # Funktion som returnerar antalet halvgarderingar.
    def get_half_count(self):
        return sum(
            value in self.HALF and not self.math_values[index]
            for index, value in enumerate(self.frame_values)
        )

    # Funktion som returnerar antalet givna matcher.
    def get_fixed_count(self):
        return sum(
            value in self.FIXED
            for value in self.frame_values
        )

    def get_fixed_allowed(self):
        return (
            self.MATCH_COUNT
            - self.full_allowed
            - self.half_allowed
            - sum(self.math_values)
        )

    def update_mathematical(self, values):
        self.math_values = list(values)

    def set_mathematical(self, match_number, value):
        self.math_values[match_number - 1] = value

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
    def get_allowed_values(self, row):
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

    # Funktion som kontrollerar om tipssystemet är giltigt.
    def validate(self):
        return (
            self.get_full_count() <= self.full_allowed
            and
            self.get_half_count() <= self.half_allowed
            and
            self.get_fixed_count() <= self.fixed_allowed
        )
