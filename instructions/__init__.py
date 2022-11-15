from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'instructions'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gave_consent = models.BooleanField(initial=False,
                                       widget=widgets.CheckboxInput,
                                       label="Ich habe die Informationen gelesen, bin einverstanden und möchte ausdrücklich an der Studie teilnehmen.")

    accepts_payment_rule = models.BooleanField(initial=False,
                                               widget=widgets.CheckboxInput,
                                               label="Ich bin mir bewusst, dass ich an allen vier Terminen teilnehmen muss, um eine Auszahlung zu erhalten.")


# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = ['gave_consent']


class GeneralInstructions(Page):
    form_model = 'player'
    form_fields = ['accepts_payment_rule']


page_sequence = [
    Consent,
    GeneralInstructions
]
