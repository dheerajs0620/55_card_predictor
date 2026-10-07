import pygame


# FIX: single source of truth for the true rank hierarchy.
# Comparing rank strings directly is lexicographic ("10" < "2" because "1" < "2"),
# so every comparison must go through these numeric values instead.
RANK_VALUES = {
    "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14,
}


class Card:

    # numeric_rank is now optional: if Deck passes it, it is used as-is;
    # otherwise it is looked up from RANK_VALUES so it can never be missing/wrong.
    def __init__(self, rank_str, suit_str, numeric_rank=None):
        self.rank_str = rank_str
        self.suit_str = suit_str
        self.numeric_rank = numeric_rank if numeric_rank is not None else RANK_VALUES[rank_str]

        self.symbol = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}.get(suit_str, "")
        self.is_red = suit_str in ("Hearts", "Diamonds")
        self.color = (220, 40, 40) if self.is_red else (30, 30, 30)

    # FIX: comparison operators based on numeric_rank, so `card_a > card_b`
    # follows 2 < ... < 10 < J < Q < K < A. Suit is ignored (rank-only game).
    # __eq__ is intentionally NOT overridden, so cards keep normal identity
    # behaviour (hashing, `in` checks); use `.numeric_rank ==` for rank ties.
    def __lt__(self, other):
        return self.numeric_rank < other.numeric_rank

    def __gt__(self, other):
        return self.numeric_rank > other.numeric_rank

    def render(self, surface, x, y, width=130, height=180):
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (255, 255, 255), card_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), card_rect, width=3, border_radius=10)

        font_rank = pygame.font.SysFont(None, 36)
        font_symbol = pygame.font.SysFont(None, 64)

        rank_surf = font_rank.render(self.rank_str, True, self.color)
        surface.blit(rank_surf, (x + 10, y + 8))

        symbol_surf = font_symbol.render(self.symbol, True, self.color)
        surface.blit(
            symbol_surf,
            (x + width // 2 - symbol_surf.get_width() // 2, y + height // 2 - symbol_surf.get_height() // 2),
        )

        surface.blit(rank_surf, (x + width - rank_surf.get_width() - 10, y + height - rank_surf.get_height() - 8))