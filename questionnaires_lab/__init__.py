from otree.api import *


doc = """
Questionnaire part for pre-test
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaires_lab'
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
    game_theory = models.BooleanField(choices=[(True, 'Ja'), (False, 'Nein')], label="Haben Sie an einem Kurs teilgenommen, der Spieltheorie zum Thema hatte?")
    risk_attitude = models.IntegerField(choices=list(range(0, 11)), label="Wie schätzen Sie sich persönlich ein: Sind Sie im Allgemeinen ein risikobereiter Mensch oder versuchen Sie, Risiken zu vermeiden? (0 = gar nicht risikobereit / 10 = sehr risikobereit)")

    iban = models.StringField(required=True, label="IBAN:")
    iban_wdh = models.StringField(required=True, label="IBAN (wiederholen):")

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
    def before_next_page(player: Player, timeout_happened):
        set_indicators(player)


class Payments(Page):
    form_model = 'player'
    form_fields = ['iban', 'iban_wdh']

    @staticmethod
    def error_message(player, values):
        if values['iban'] != values['iban_wdh']:
            return 'Die IBANs stimmen nicht überein.'

class LastPage(Page):
    pass

page_sequence = [Demographics, Payments, LastPage]
