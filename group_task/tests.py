from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield GroupSelection, dict(group_number=self.player.id_in_subsession)
        yield GroupAnnouncement
        yield GroupTask1
        yield GroupTask2, dict(individual_ideas="A long list of items.")
        yield GroupTask3, dict(group_ideas="An even longer list of items.")
        yield Submission(LastPage, check_html=False)