from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        week = self.session.config['week']

        if week == 1:
            yield Consent, dict(gave_consent=True)
            yield GeneralInstructions, dict(accepts_payment_rule=True)

        else:
            yield InstructionReminder
