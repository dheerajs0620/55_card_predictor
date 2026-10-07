import pygame
from game.deck import Deck

class GameEngine:
    BASE_POINTS = 1  # TASK 2: points for a correct guess before the streak multiplier
    REVEAL_MS = 1200  # TASK 4: how long both cards stay on screen before the next round
    CARD_W, CARD_H = 130, 180

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.deck = Deck()

        self.current_card = self.deck.draw()
        self.next_card = None
        self.score = 0
        self.streak_count = 0  # TASK 2: consecutive correct guesses
        self.status_msg = "Will the next card be HIGHER or LOWER?"
        self.status_color = (220, 220, 220)

        # TASK 4: reveal-phase state. While `revealing` is True the new card is
        # shown next to the previous one and all input is ignored.
        self.revealing = False
        self.reveal_elapsed = 0

        # TASK 4: two card slots side by side, centred as a pair
        gap = 60
        self.left_x = width // 2 - self.CARD_W - gap // 2
        self.right_x = width // 2 + gap // 2
        self.card_y = 100

        btn_w, btn_h = 140, 48
        self.btn_higher = pygame.Rect(width // 2 - btn_w - 20, height - 90, btn_w, btn_h)
        self.btn_lower = pygame.Rect(width // 2 + 20, height - 90, btn_w, btn_h)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_medium = pygame.font.SysFont(None, 30)
        self.font_small = pygame.font.SysFont(None, 24)

    def evaluate_guess(self, guess):
        """Draws next card and evaluates prediction."""
        # TASK 4: ignore guesses during the reveal (also guards against double-clicks)
        if self.revealing:
            return

        self.next_card = self.deck.draw()
        
        cur = self.current_card.numeric_rank
        nxt = self.next_card.numeric_rank

        # TASK 3: a tie is a PUSH. Score and streak stay untouched, and the
        # round is neither a win nor a loss. Checked first so ties never reach
        # the HIGHER/LOWER comparison below (where they would count as wrong).
        if nxt == cur:
            self.status_msg = f"PUSH! {self.next_card.rank_str} equals {self.current_card.rank_str}"
            self.status_color = (230, 230, 120)  # neutral yellow: not green, not red
        else:
            # FIX: compare numeric ranks (2..14), not rank_str (lexicographic)
            if guess == "HIGHER":
                correct = nxt > cur
            else:
                correct = nxt < cur

            if correct:
                # TASK 2: extend the streak, then use it as the multiplier
                self.streak_count += 1
                points = self.BASE_POINTS * self.streak_count
                self.score += points
                self.status_msg = (
                    f"CORRECT! +{points} (x{self.streak_count}) "
                    f"{self.next_card.rank_str} vs {self.current_card.rank_str}"
                )
                self.status_color = (80, 220, 80)
            else:
                # TASK 2: a wrong guess resets the streak (ties no longer land here)
                self.streak_count = 0
                self.score = max(0, self.score - 1)
                self.status_msg = f"WRONG! {self.next_card.rank_str} vs {self.current_card.rank_str}"
                self.status_color = (235, 75, 75)

        # TASK 4: do NOT swap current_card here any more. The old card stays on
        # the left and the new one appears on the right until update() ends the reveal.
        self.revealing = True
        self.reveal_elapsed = 0

    def handle_event(self, event):
        # TASK 4: buttons are disabled while the reveal is running
        if self.revealing:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_higher.collidepoint(event.pos):
                self.evaluate_guess("HIGHER")
            elif self.btn_lower.collidepoint(event.pos):
                self.evaluate_guess("LOWER")

    def update(self, dt=0):
        """dt = milliseconds since the last frame (main.py passes clock.tick())."""
        # TASK 4: count the reveal down, then advance to the next round
        if self.revealing:
            self.reveal_elapsed += dt
            if self.reveal_elapsed >= self.REVEAL_MS:
                self.current_card = self.next_card  # drawn card becomes the new "current"
                self.next_card = None
                self.revealing = False

    def _draw_card_back(self, screen, x, y):
        """TASK 4: face-down placeholder for the not-yet-drawn card."""
        rect = pygame.Rect(x, y, self.CARD_W, self.CARD_H)
        pygame.draw.rect(screen, (40, 70, 140), rect, border_radius=10)
        pygame.draw.rect(screen, (230, 230, 230), rect, width=3, border_radius=10)
        q = self.font_title.render("?", True, (230, 230, 230))
        screen.blit(q, (rect.centerx - q.get_width() // 2, rect.centery - q.get_height() // 2))

    def render(self, screen):
        screen.fill((25, 80, 45))

        title_surf = self.font_title.render("High-Low Card Predictor", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (30, 30))

        # TASK 2: streak + the multiplier the NEXT correct guess will earn
        streak_surf = self.font_small.render(
            f"Streak: {self.streak_count}  |  Next win: x{self.streak_count + 1}",
            True,
            (255, 190, 90) if self.streak_count else (210, 210, 210),
        )
        screen.blit(streak_surf, (30, 62))

        rem_surf = self.font_small.render(f"Deck: {self.deck.remaining} left", True, (210, 210, 210))
        screen.blit(rem_surf, (self.width - rem_surf.get_width() - 30, 35))

        # TASK 4: left = previous/current card, right = newly drawn card
        # (face-down "?" until a guess is made)
        self.current_card.render(screen, self.left_x, self.card_y, self.CARD_W, self.CARD_H)
        if self.revealing:
            self.next_card.render(screen, self.right_x, self.card_y, self.CARD_W, self.CARD_H)
            left_label, right_label = "Previous", "Drawn"
        else:
            self._draw_card_back(screen, self.right_x, self.card_y)
            left_label, right_label = "Current", "Next"

        for label, x in ((left_label, self.left_x), (right_label, self.right_x)):
            lab = self.font_small.render(label, True, (210, 210, 210))
            screen.blit(lab, (x + self.CARD_W // 2 - lab.get_width() // 2, self.card_y + self.CARD_H + 6))

        status_surf = self.font_small.render(self.status_msg, True, self.status_color)
        screen.blit(status_surf, (self.width // 2 - status_surf.get_width() // 2, 325))

        # TASK 4: grey out both buttons while the reveal is running
        higher_col = (90, 90, 90) if self.revealing else (40, 140, 60)
        lower_col = (90, 90, 90) if self.revealing else (170, 50, 50)
        text_col = (160, 160, 160) if self.revealing else (255, 255, 255)

        pygame.draw.rect(screen, higher_col, self.btn_higher, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), self.btn_higher, width=2, border_radius=8)
        high_surf = self.font_medium.render("HIGHER", True, text_col)
        screen.blit(
            high_surf,
            (self.btn_higher.centerx - high_surf.get_width() // 2, self.btn_higher.centery - high_surf.get_height() // 2),
        )

        pygame.draw.rect(screen, lower_col, self.btn_lower, border_radius=8)
        pygame.draw.rect(screen, (220, 220, 220), self.btn_lower, width=2, border_radius=8)
        low_surf = self.font_medium.render("LOWER", True, text_col)
        screen.blit(
            low_surf,
            (self.btn_lower.centerx - low_surf.get_width() // 2, self.btn_lower.centery - low_surf.get_height() // 2),
        )