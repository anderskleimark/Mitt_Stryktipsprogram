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

    # Funktion som ställer in vilket tipssystem som används.
    def set_system(self, system):

        self.full_allowed = system.full_covers
        self.half_allowed = system.half_covers
        self.fixed_allowed = (
            self.MATCH_COUNT
            - self.full_allowed
            - self.half_allowed
        )

    # Funktion som uppdaterar ramtecknen för de tretton (13) matcherna.
    def update_frames(self, frame_values):

        self.frame_values = list(frame_values)

        while len(self.frame_values) < self.MATCH_COUNT:
            self.frame_values.append("")

    # Funktion som returnerar antalet helgarderingar.
    def get_full_count(self):

        return sum(
            value == self.FULL
            for value in self.frame_values
        )

    # Funktion som returnerar antalet halvgarderingar.
    def get_half_count(self):

        return sum(
            value in self.HALF
            for value in self.frame_values
        )

    # Funktion som returnerar antalet givna matcher.
    def get_fixed_count(self):

        return sum(
            value in self.FIXED
            for value in self.frame_values
        )

    # Funktion som returnerar statistik om systemet.
    def get_statistics(self):

        full = self.get_full_count()
        half = self.get_half_count()
        fixed = self.get_fixed_count()

        return {
            "full": full,
            "half": half,
            "fixed": fixed,
            "full_left": self.full_allowed - full,
            "half_left": self.half_allowed - half,
            "fixed_left": self.fixed_allowed - fixed
        }

    # Funktion som returnerar de ramtecken som är tillåtna för en viss match.
    def get_allowed_values(self, row):

        # Gör en kopia och bortse från aktuell match.
        frames = self.frame_values.copy()

        if 0 <= row < len(frames):
            frames[row] = ""

        full = sum(v == self.FULL for v in frames)
        half = sum(v in self.HALF for v in frames)
        fixed = sum(v in self.FIXED for v in frames)

        allowed = [
            ""
        ]

        # Givna matcher
        if fixed < self.fixed_allowed:
            allowed.extend([
                "1",
                "X",
                "2"
            ])

        # Halvgarderingar
        if half < self.half_allowed:
            allowed.extend([
                "1X",
                "12",
                "X2"
            ])

        # Helgarderingar
        if full < self.full_allowed:
            allowed.append("1X2")

        # Behåll nuvarande värde
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
