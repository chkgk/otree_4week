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


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gave_consent = models.BooleanField(initial=False,
                                       widget=widgets.CheckboxInput,
                                       label="Ich habe die Informationen gelesen, bin einverstanden und möchte ausdrücklich an der Studie teilnehmen.")

    email = models.StringField(label="E-Mail-Adresse:")

# PAGES
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


class SendOff(Page):
    pass


#FUNCTIONS
def creating_session(subsession):
    subsession.group_randomly()

def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'group_id', 'email']
    for p in players:
        participant = p.participant
        group = p.group
        session = p.session
        yield [session.code, participant.code, group.id, p.email]


page_sequence = [Consent, GeneralInstructions, TaskInstructions, Matching, SendOff]
