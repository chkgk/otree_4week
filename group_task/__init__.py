from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'group_task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    group_number = models.IntegerField(choices=[1, 2, 3, 4], label="Group number:")

    individual_ideas = models.LongStringField(label="Ideensammlung der einzelnen Gruppenmitglieder:")
    group_ideas = models.LongStringField(label="Ideensammlung der Gruppe:")


# PAGES
class GroupSelection(Page):
    form_model = 'player'
    form_fields = ['group_number']


class GroupAnnouncement(Page):
    pass


class GroupTask1(Page):
    def js_vars(player: Player):
        return dict(timeout_seconds=3*60)


class GroupTask2(Page):
    form_model = 'player'
    form_fields = ['individual_ideas']
    
    def js_vars(player: Player):
        return dict(timeout_seconds=5*60)


class GroupTask3(Page):
    form_model = 'player'
    form_fields = ['group_ideas']
    
    def js_vars(player: Player):
        return dict(timeout_seconds=10*60)


class LastPage(Page):
    pass

page_sequence = [GroupSelection, GroupAnnouncement, GroupTask1, GroupTask2, GroupTask3, LastPage]
