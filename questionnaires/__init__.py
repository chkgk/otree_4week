from otree.api import *


doc = """
Questionnaire part for pre-test
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaires'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(min=0, max=120, label="Wie alt sind Sie (Jahre)?")
    gender = models.StringField(choices=['weiblich', 'männlich', 'anderes', 'keine Angabe'], label="Was ist Ihr Geschlecht?", widget=widgets.RadioSelect)
    economics = models.BooleanField(choices=[(True, 'Ja'), (False, 'Nein')], label="Studieren Sie Betriebswirtschaftslehre oder Volkswirtschaftslehre?")
    game_theory = models.BooleanField(choices=[(True, 'Ja'), (False, 'Nein')], label="Haben Sie schon einmal eine Spieltheorievorlesung gehört?")
    risk_attitude = models.IntegerField(choices=list(range(0, 11)), label="Wie schätzen Sie sich persönlich ein: Sind Sie im Allgemeinen ein risikobereiter Mensch oder versuchen Sie, Risiken zu vermeiden? (0 = gar nicht risikobereit / 10 = sehr risikobereit)", widget=widgets.RadioSelectHorizontal)

    # indicators
    female = models.BooleanField()
    male = models.BooleanField()
    other_gender = models.BooleanField()
    na_gender = models.BooleanField()


# FUNCTIONS
def set_indicators(player: Player):
    player.female = player.gender == 'weiblich'
    player.male = player.gender == 'männlich'
    player.other_gender = player.gender == 'anderes'
    player.na_gender = player.gender == 'keine Angabe'


# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'economics', 'game_theory', 'risk_attitude']

    @staticmethod
    def is_displayed(player: Player):
        return player.session.config.get('week', 1) == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        set_indicators(player)


class LastPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(week=player.session.config.get('week', 1))


page_sequence = [Demographics, LastPage]
