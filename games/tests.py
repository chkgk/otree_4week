from otree.api import currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        if self.round_number == self.participant.task_rounds['dictator']:
            yield Submission(DictatorIntro, check_html=False)
            yield Dictator1
            yield Dictator2, dict(dictator_amount_sent=60)

        if self.round_number == self.participant.task_rounds['trust_game']:
            yield Submission(TrustIntro, check_html=False)
            yield Trust1

            if self.participant.trust_sender_this_week:
                yield TrustP1, dict(trust_p1_sent=80)
            else:
                yield TrustP2, {
                    'trust_p2_sent_1': 50,
                    'trust_p2_sent_2': 50,
                    'trust_p2_sent_3': 50,
                    'trust_p2_sent_4': 50,
                    'trust_p2_sent_5': 50,
                    'trust_p2_sent_6': 50,
                    'trust_p2_sent_7': 50,
                    'trust_p2_sent_8': 50,
                    'trust_p2_sent_9': 50,
                    'trust_p2_sent_10': 50
                }

        if self.round_number == self.participant.task_rounds['public_good']:
            yield Submission(PublicIntro, check_html=False)
            yield Public1
            yield Public2, dict(public_contribution=40)

        if self.round_number == self.participant.task_rounds['minimum_effort']:
            yield Submission(MinimumIntro, check_html=False)
            yield Minimum1
            yield Minimum2, dict(minimum_number_selected=70)

        if self.round_number == 4:
            part = self.participant

            # Dictator Game (keeps 140, sends 60)
            expect(part.dictator_payoff_set, True)
            if part.dictator_this_week:
                expect(part.dictator_payoff, 140)
            else:
                expect(part.dictator_payoff, 60)

            # Trust Game (P1 sends 80, P2 returns 50% always)
            expect(part.trust_payoff_set, True)
            if part.trust_sender_this_week:
                expect(part.trust_payoff, 20 + 80*3*0.5)
            else:
                expect(part.trust_payoff, 100 + 120)

            # Public Good Game (P1 and P2 contribute 40)
            # should add test with different contributions
            expect(part.public_payoff_set, True)
            expect(part.public_payoff, 100 - 40 + C.PUBLIC_MPCR * (40+40))

            # Minimum Effort Game (both choose 70)
            # should add test for different choices
            expect(part.minimum_payoff_set, True)
            expect(part.minimum_payoff, 85)