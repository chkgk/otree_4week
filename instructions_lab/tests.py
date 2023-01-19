from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield SeatNumber, dict(seat_number=self.player.id_in_subsession)
        yield Consent, dict(gave_consent=True)
        yield GeneralInstructions, dict(email=f"player{self.player.id_in_subsession}@example.com", name="Christian König")
        yield Submission(TaskInstructions, check_html=False)
        yield Submission(SendOff, check_html=False)
