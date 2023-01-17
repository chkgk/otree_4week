import otree.settings
from otree.api import *
import random
import math

doc = """
Games over 4 weeks, by Christian König-Kersting
"""


class C(BaseConstants):
    NAME_IN_URL = 'games_lab'
    PLAYERS_PER_GROUP = 6
    GAMES = ['dictator', 'trust_game', 'public_good', 'minimum_effort']
    NUM_ROUNDS = len(GAMES)

    SPLASH_SECONDS = 3
    SPLASH_TEMPLATE = 'games/Splashscreen.html'

    DICTATOR_ENDOWMENT = cu(200)

    TRUST_ENDOWMENT = cu(100)
    TRUST_MULTIPLIER = 3

    PUBLIC_ENDOWMENT = cu(100)
    PUBLIC_MPCR = 0.8

    MINIMUM_MAX_NUMBER = 100
    MINIMUM_P1 = 1
    MINIMUM_P2 = 0.5
    
    GROUP_MAP = {
        'ga': 1,
        'gb': 2,
        'gc': 3,
        'gd': 4
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    group_number = models.IntegerField()
    
    dictator_amount_sent = models.CurrencyField(min=0, max=C.DICTATOR_ENDOWMENT, label="Wie viele Punkte möchten Sie dem anderen Spieler geben?")

    trust_p1_sent = models.CurrencyField(min=0, max=C.TRUST_ENDOWMENT, label="Wie viele Punkte möchten Sie an den anderen Spieler senden?")

    trust_p2_sent_1 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen 0 und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10} erhalten?")
    trust_p2_sent_2 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*2} erhalten?")
    trust_p2_sent_3 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*2+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*3} erhalten?")
    trust_p2_sent_4 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*3+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*4} erhalten?")
    trust_p2_sent_5 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*4+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*5} erhalten?")
    trust_p2_sent_6 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*5+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*6} erhalten?")
    trust_p2_sent_7 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*6+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*7} erhalten?")
    trust_p2_sent_8 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*7+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*8} erhalten?")
    trust_p2_sent_9 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*8+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*9} erhalten?")
    trust_p2_sent_10 = models.IntegerField(min=0, max=100, label=f"...wenn Sie zwischen {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT/10*9+1} und {C.TRUST_MULTIPLIER*C.TRUST_ENDOWMENT} erhalten?")

    public_contribution = models.CurrencyField(min=0, max=C.PUBLIC_ENDOWMENT, label="Wie viele Punkte möchten Sie zum öffentlichen Gut beisteuern?")

    minimum_number_selected = models.IntegerField(min=0, max=C.MINIMUM_MAX_NUMBER, label=f"Wählen Sie eine Zahl zwischen 0 und {C.MINIMUM_MAX_NUMBER}!")


class ParticipantConfig(ExtraModel):
    session_code = models.StringField()
    id_in_subsession = models.IntegerField()
    participant_label = models.StringField()
    group_id = models.IntegerField()
    email = models.StringField()


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

        with open(subsession.session.config.get('labels', '_rooms/pilot1.txt')) as f:
            labels = [l.strip() for l in f.readlines()]
        for p, label in zip(subsession.get_players(), labels):
            p.participant.label = label

        group_matrix = dict()
        for p in subsession.get_players():
            part = p.participant

            part.dictator_payoff_set = False
            part.trust_payoff_set = False
            part.public_payoff_set = False
            part.minimum_payoff_set = False
            part.is_finished = False
            part.week_payoff_set = False
            part.pay_game = random.choice(['dictator', 'trust', 'public', 'minimum'])
            part.final_payoff = 0.0

            gn = C.GROUP_MAP[part.label[-2:]]
            if not group_matrix.get(gn, False):
                group_matrix[gn] = [p.id_in_subsession]
            else:
                group_matrix[gn].append(p.id_in_subsession)

        subsession.set_group_matrix([l for _, l in group_matrix.items()])


def _get_partner(player, game):
    partner = None
    if player.participant.pos_in_group < 4:
        partner_pos = player.participant.pos_in_group + 3
    else:
        partner_pos = player.participant.pos_in_group - 3

    for p in player.group.get_players():
        if p.participant.pos_in_group == partner_pos:
            partner = p.in_round(p.participant.task_rounds.get(game, 1))
    return partner


def calculate_payoffs(player: Player):
    player.participant.is_finished = True

    calculate_dictator_payoff(player)
    calculate_trust_payoff(player)
    calculate_public_payoff(player)
    calculate_minimum_payoff(player)

    # run determine week payoffs for everyone
    for p in player.subsession.get_players():
        determine_week_payoff(p)


def calculate_dictator_payoff(player: Player):
    part = player.participant
    if part.dictator_payoff_set:
        return

    if part.dictator_this_week:
        dictator_round = part.task_rounds['dictator']
        part.dictator_decision = player.in_round(dictator_round).dictator_amount_sent
        part.dictator_payoff = C.DICTATOR_ENDOWMENT - player.in_round(dictator_round).dictator_amount_sent
        part.dictator_payoff_set = True

        partner = _get_partner(player, 'dictator')
        # print(player.id_in_subsession, partner)
        partner.participant.dictator_payoff = player.in_round(dictator_round).dictator_amount_sent
        partner.participant.dictator_payoff_set = True


def calculate_trust_payoff(player: Player):
    part = player.participant

    if part.trust_payoff_set:
        return

    myself = player.in_round(part.task_rounds['trust_game'])
    other = _get_partner(player, 'trust_game')

    if not all([myself.participant.is_finished, other.participant.is_finished]):
        return

    if part.trust_sender_this_week:
        p1, p2 = myself, other
    else:
        p1, p2 = other, myself

    p1_decision, p1_payoff, p2_decision, p2_payoff = _trust_game_payoff(p1, p2)

    p1.participant.trust_decision = p1_decision
    p2.participant.trust_decision = p2_decision

    p1.participant.trust_payoff = p1_payoff
    p2.participant.trust_payoff = p2_payoff

    p1.participant.trust_payoff_set = True
    p2.participant.trust_payoff_set = True


def _trust_game_payoff(p1, p2):
    p1_sends = p1.trust_p1_sent
    p2_receives = p1_sends * C.TRUST_MULTIPLIER

    if 0 <= p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10:
        p2_sends_back = p2.trust_p2_sent_1
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 2:
        p2_sends_back = p2.trust_p2_sent_2
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 2 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 3:
        p2_sends_back = p2.trust_p2_sent_3
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 3 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 4:
        p2_sends_back = p2.trust_p2_sent_4
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 4 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 5:
        p2_sends_back = p2.trust_p2_sent_5
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 5 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 6:
        p2_sends_back = p2.trust_p2_sent_6
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 6 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 7:
        p2_sends_back = p2.trust_p2_sent_7
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 7 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 8:
        p2_sends_back = p2.trust_p2_sent_8
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 8 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 9:
        p2_sends_back = p2.trust_p2_sent_9
    elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 9 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT:
        p2_sends_back = p2.trust_p2_sent_10
    else:
        p2_sends_back = 0

    p1_payoff = C.TRUST_ENDOWMENT - p1_sends + math.floor(p2_sends_back/100 * p2_receives)
    p2_payoff = C.TRUST_ENDOWMENT + p2_receives - math.floor(p2_sends_back/100 * p2_receives)

    return p1_sends, p1_payoff, p2_sends_back, p2_payoff


def calculate_public_payoff(player: Player):
    part = player.participant

    if part.public_payoff_set:
        return

    myself = player.in_round(part.task_rounds['public_good'])
    other = _get_partner(player, 'public_good')

    if not all([myself.participant.is_finished, other.participant.is_finished]):
        return

    public_good_pot = myself.public_contribution + other.public_contribution

    part.public_decision = myself.public_contribution
    other.participant.public_decision = other.public_contribution

    part.public_payoff = C.PUBLIC_ENDOWMENT - myself.public_contribution + C.PUBLIC_MPCR * public_good_pot
    other.participant.public_payoff = C.PUBLIC_ENDOWMENT - other.public_contribution + C.PUBLIC_MPCR * public_good_pot

    part.public_payoff_set = True
    other.participant.public_payoff_set = True


def calculate_minimum_payoff(player: Player):
    part = player.participant

    if part.minimum_payoff_set:
        return

    myself = player.in_round(part.task_rounds['minimum_effort'])
    other = _get_partner(player, 'minimum_effort')

    if not all([myself.participant.is_finished, other.participant.is_finished]):
        return

    my_number = myself.minimum_number_selected
    others_number = other.minimum_number_selected

    if my_number >= others_number:
        my_payoff = C.MINIMUM_P1 * others_number + C.MINIMUM_P2 * (C.MINIMUM_MAX_NUMBER - my_number)
        others_payoff = C.MINIMUM_P1 * my_number + C.MINIMUM_P2 * (C.MINIMUM_MAX_NUMBER - others_number)
    else:
        my_payoff = C.MINIMUM_P1 * my_number + C.MINIMUM_P2 * (C.MINIMUM_MAX_NUMBER - others_number)
        others_payoff = C.MINIMUM_P1 * others_number + C.MINIMUM_P2 * (C.MINIMUM_MAX_NUMBER - my_number)

    part.minimum_decision = my_number
    other.participant.minimum_decision = others_number

    part.minimum_payoff = my_payoff
    other.participant.minimum_payoff = others_payoff

    part.minimum_payoff_set = True
    other.participant.minimum_payoff_set = True


def determine_week_payoff(player: Player):
    part = player.participant
    if part.week_payoff_set:
        return

    if not all([part.dictator_payoff_set, part.trust_payoff_set, part.minimum_payoff_set, part.public_payoff_set]):
        return

    player.payoff = part.vars.get(f"{part.pay_game}_payoff", 0)
    part.week_payoff = player.payoff
    part.week_payoff_set = True

    part.final_payoff = cu(part.week_payoff).to_real_world_currency(player.session) + player.session.config.get('participation_fee', 0.0)
    part.finished = 1


def set_role(player):
    started_participants = sum([p.participant._index_in_pages > 1 for p in player.group.get_players()])
    player.participant.pos_in_group = started_participants + 1

    if started_participants < 3:
        player.participant.dictator_this_week = True
        player.participant.trust_sender_this_week = True
    else:
        player.participant.dictator_this_week = False
        player.participant.trust_sender_this_week = False

# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def before_next_page(player: Player, timeout_happened):
        set_role(player)

class DictatorIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['dictator']

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='D')


class Dictator1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['dictator']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='D')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=C.DICTATOR_ENDOWMENT
        )


class Dictator2(Page):
    form_model = 'player'
    form_fields = ['dictator_amount_sent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['dictator']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='D')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=C.DICTATOR_ENDOWMENT
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 4:
            calculate_payoffs(player)


class TrustIntro(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='T')

    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE


class Trust1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='T')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=C.TRUST_ENDOWMENT,
            multiplier=C.TRUST_MULTIPLIER
        )


class TrustP1(Page):
    form_model = 'player'
    form_fields = ['trust_p1_sent']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game'] and player.participant.trust_sender_this_week

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='T')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=C.TRUST_ENDOWMENT,
            multiplier=C.TRUST_MULTIPLIER
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 4:
            calculate_payoffs(player)


class TrustP2(Page):
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

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['trust_game'] and not player.participant.trust_sender_this_week

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='T')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            endowment=C.TRUST_ENDOWMENT,
            multiplier=C.TRUST_MULTIPLIER
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 4:
            calculate_payoffs(player)


class PublicIntro(Page):
    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['public_good']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='P')


class Public1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['public_good']

    @staticmethod
    def js_vars(player: Player):
        return dict(
            mpcr=C.PUBLIC_MPCR,
            endowment=C.PUBLIC_ENDOWMENT
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            multiplier=C.PUBLIC_MPCR * 2,
            endowment=C.PUBLIC_ENDOWMENT,
            spiel='P'
        )


class Public2(Page):
    form_model = 'player'
    form_fields = ['public_contribution']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['public_good']

    @staticmethod
    def js_vars(player: Player):
        return dict(
            mpcr=C.PUBLIC_MPCR,
            endowment=C.PUBLIC_ENDOWMENT
        )

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            multiplier=C.PUBLIC_MPCR * 2,
            endowment=C.PUBLIC_ENDOWMENT,
            spiel='P'
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 4:
            calculate_payoffs(player)


class MinimumIntro(Page):
    timeout_seconds = C.SPLASH_SECONDS
    template_name = C.SPLASH_TEMPLATE

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['minimum_effort']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='M')


class Minimum1(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['minimum_effort']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='M')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            max_number=C.MINIMUM_MAX_NUMBER,
            p1=C.MINIMUM_P1,
            p2=C.MINIMUM_P2
        )


class Minimum2(Page):
    form_model = 'player'
    form_fields = ['minimum_number_selected']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.participant.task_rounds['minimum_effort']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(spiel='M')

    @staticmethod
    def js_vars(player: Player):
        return dict(
            max_number=C.MINIMUM_MAX_NUMBER,
            p1=C.MINIMUM_P1,
            p2=C.MINIMUM_P2
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.round_number == 4:
            calculate_payoffs(player)


page_sequence = [
    Introduction,
    DictatorIntro,
    Dictator1,
    Dictator2,
    TrustIntro,
    Trust1,
    TrustP1,
    TrustP2,
    PublicIntro,
    Public1,
    Public2,
    MinimumIntro,
    Minimum1,
    Minimum2
]
