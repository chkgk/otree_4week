from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        week = self.session.config['week']

        if week == 1:
            yield Demographics, {
                'age': random.randint(18, 80),
                'gender': random.choice(['weiblich', 'männlich', 'anderes', 'keine Angabe']),
                'economics': random.choice([True, False]),
                'game_theory': random.choice([True, False]),
                'risk_attitude': random.randint(0, 10)
            }
            yield Payments, dict(iban="asdf", iban_wdh="asdf")
            expect('Am nächsten Dienstag', 'in', self.html)
            yield Submission(LastPage, check_html=False)

        else:
            if week == 4:
                expect('In ungefähr einer', 'in', self.html)
            yield Submission(LastPage, check_html=False)
