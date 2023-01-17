from otree.api import *
import random
import string   

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions_lab'
    PLAYERS_PER_GROUP = 6
    NUM_ROUNDS = 1

    BRAINSTORMING_MINUTES = 1 # reset to 7

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
    gave_consent = models.BooleanField(initial=False,
                                       widget=widgets.CheckboxInput,
                                       label="Ich habe die Informationen gelesen, bin einverstanden und möchte ausdrücklich an der Studie teilnehmen.")

    email = models.StringField(label="E-Mail-Adresse:")
    seat_number = models.IntegerField(label="Bitte geben Sie Ihre Sitzplatznummer ein.", min=1, max=24)
    group_number = models.IntegerField()
    label = models.StringField()

# PAGES
class SeatNumber(Page):
    form_model = 'player'
    form_fields = ['seat_number']


class Consent(Page):
    form_model = 'player'
    form_fields = ['gave_consent']


class GeneralInstructions(Page):
    form_model = 'player'
    form_fields = ['email']


class TaskInstructions(Page):
    timeout_seconds = C.BRAINSTORMING_MINUTES * 60


class Matching(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = 'match_groups'


class SendOff(Page):
    pass


#FUNCTIONS
def match_groups(subsession):
    with open(subsession.session.config.get('labels', '_rooms/pilot1.txt')) as f:
        labels = [l.strip() for l in f.readlines()]
    players = sorted(subsession.get_players(), key=lambda x: x.seat_number)

    group_matrix = dict()
    for p, label in zip(players, labels):
        p.label = label
    
        gn = C.GROUP_MAP[p.label[-2:]]
        p.group_number = gn
        #print(p, label, gn)
        if not group_matrix.get(gn, False):
            group_matrix[gn] = [p.id_in_subsession]
        else:
            group_matrix[gn].append(p.id_in_subsession)
    subsession.set_group_matrix([v for _, v in group_matrix.items()])


def custom_export(players):
    # header row
    yield ['session_code', 'id_in_subsession', 'participant_label', 'group_id', 'email']
    for p in players:
        participant = p.participant
        group = p.group
        session = p.session
        yield [session.code, p.id_in_subsession, p.label, p.group_number, p.email]


page_sequence = [SeatNumber, Consent, GeneralInstructions, TaskInstructions, Matching, SendOff]
