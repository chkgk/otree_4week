import otree.settings
from otree.api import *
import random


doc = """
Games over 4 weeks, by Christian König-Kersting
"""


class C(BaseConstants):
    NAME_IN_URL = 'games'
    PLAYERS_PER_GROUP = 2
    GAMES = ['dictator', 'trust_game', 'public_good', 'minimum_effort']
    NUM_ROUNDS = len(GAMES)

    SPLASH_SECONDS = 3
    SPLASH_TEMPLATE = 'games/Splashscreen.html'

    DICTATOR_ENDOWMENT = cu(200)
    TRUST_ENDOWMENT = cu(100)
    TRUST_MULTIPLIER = 3
    PUBLIC_ENDOWMMENT = cu(100)
    PUBLIC_MPCR = 0.7
    MINIMUM_MAX_NUMBER = 100


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    dictator_amount_sent = models.CurrencyField(min=0, max=C.DICTATOR_ENDOWMENT, label="Wie viele Punkte möchten Sie dem anderen Spieler geben?")

    trust_p1_sent = models.CurrencyField(min=0, max=C.TRUST_ENDOWMENT, label="Wie viele Punkte möchten Sie an den anderen Spieler senden?")

    trust_p2_sent_1 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10, label=f"...wenn Sie zwischen 0 und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10} erhalten?")
    trust_p2_sent_2 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*2, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*2} erhalten?")
    trust_p2_sent_3 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*3, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*2+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*3} erhalten?")
    trust_p2_sent_4 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*4, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*3+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*4} erhalten?")
    trust_p2_sent_5 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*5, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*4+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*5} erhalten?")
    trust_p2_sent_6 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*6, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*5+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*6} erhalten?")
    trust_p2_sent_7 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*7, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*6+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*7} erhalten?")
    trust_p2_sent_8 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*8, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*7+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*8} erhalten?")
    trust_p2_sent_9 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*9, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*8+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*9} erhalten?")
    trust_p2_sent_10 = models.CurrencyField(min=0, max=C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*9+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT} erhalten?")

    public_contribution = models.CurrencyField(min=0, max=C.PUBLIC_ENDOWMMENT, label="Wie viele Punkte möchten Sie zum öffentlichen Gut beisteuern?")

    minimum_number_selected = models.IntegerField(min=0, max=C.MINIMUM_MAX_NUMBER, label=f"Wählen Sie eine Zahl zwischen 0 und {C.MINIMUM_MAX_NUMBER}!")


# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        if otree.settings.DEBUG:
            for p in subsession.get_players():
                p.participant.task_rounds = {'dictator': 1, 'trust_game': 2, 'public_good': 3, 'minimum_effort': 4}
        else:
            for p in subsession.get_players():
                round_numbers = list(range(1, C.NUM_ROUNDS + 1))
                random.shuffle(round_numbers)
                task_rounds = dict(zip(C.GAMES, round_numbers))
                # print('player', p.id_in_subsession)
                # print('task_rounds is', task_rounds)
                p.participant.task_rounds = task_rounds


# PAGES
class DictatorIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['dictator']

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE


class Dictator1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['dictator']

    form_model = 'player'
    form_fields = ['dictator_amount_sent']


class TrustIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game']

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE


class Trust1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game'] and player.id_in_group == 1

    form_model = 'player'
    form_fields = ['trust_p1_sent']


class Trust2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game'] and player.id_in_group == 2

    form_model = 'player'
    form_fields = [
        'trust_p2_sent_1',
        'trust_p2_sent_2',
        'trust_p2_sent_3',
        'trust_p2_sent_4',
        'trust_p2_sent_5',
        'trust_p2_sent_6',
        'trust_p2_sent_7',
        'trust_p2_sent_8',
        'trust_p2_sent_9',
        'trust_p2_sent_10',
    ]


class PublicIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['public_good']

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE


class Public1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['public_good']

    form_model = 'player'
    form_fields = ['public_contribution']


class MinimumIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['minimum_effort']

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE


class Minimum1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['minimum_effort']

    form_model = 'player'
    form_fields = ['minimum_number_selected']


page_sequence = [
    # DictatorIntro,
    Dictator1,
    # TrustIntro,
    Trust1,
    Trust2,
    # PublicIntro,
    Public1,
    # MinimumIntro,
    Minimum1,
]
