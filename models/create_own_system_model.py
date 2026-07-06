from mvc import Model
import random
from itertools import product


class CreateOwnSystemModel(Model):
    GAMES = 13

    def __init__(self):
        super().__init__()

    def get_max_half_cover(self, full_cover):
        return self.GAMES - full_cover

    def get_max_full_cover(self, half_cover):
        return self.GAMES - half_cover

    def create_system(self, full_cover, half_cover, guarantee, rows):
        # 13 matcher i Stryktipset
        matches = list(range(13))

        # välj vilka matcher som är hel/halv
        full_positions = set(random.sample(matches, full_cover))
        remaining = [m for m in matches if m not in full_positions]
        half_positions = set(random.sample(remaining, half_cover))

        # resterande blir singlar
        single_positions = [
            m for m in matches
            if m not in full_positions and m not in half_positions
        ]

        system_rows = []

        # generera alla kombinationer
        # hel = 1X2, halv = 1X eller X2, singel = 1
        def options_for(pos):
            if pos in full_positions:
                return ["1", "X", "2"]
            elif pos in half_positions:
                return ["1", "X"]
            else:
                return ["1"]

        all_options = [options_for(i) for i in range(13)]

        all_combinations = list(product(*all_options))

        # begränsa antal rader
        random.shuffle(all_combinations)
        selected = all_combinations[:rows]

        system_rows = [list(r) for r in selected]

        return {
            "rows": system_rows,
            "full_cover": full_cover,
            "half_cover": half_cover,
            "guarantee": guarantee,
            "total_rows": len(system_rows)
        }
