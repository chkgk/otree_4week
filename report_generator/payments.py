import random


DICTATOR_ENDOWMENT = 200
PUBLIC_ENDOWMENT = 100
PUBLIC_MPCR = 0.8

MINIMUM_MAX_NUMBER = 100
MINIMUM_P1 = 0.1
MINIMUM_P2 = 0.05

k = ['participant.id_in_session', 'participant.code', 'participant.label', 'participant.visited', 'participant.payoff',
     'participant.task_rounds', 'participant.dictator_1', 'participant.dictator_2', 'participant.dictator_3',
     'participant.dictator_4', 'participant.dictator_this_week', 'participant.dictator_payoff_set',
     'participant.dictator_payoff', 'participant.trust_sender_1', 'participant.trust_sender_2',
     'participant.trust_sender_3', 'participant.trust_sender_4', 'participant.trust_sender_this_week',
     'participant.trust_payoff_set', 'participant.trust_payoff', 'participant.partner_id_1', 'participant.partner_id_2',
     'participant.partner_id_3', 'participant.partner_id_4', 'participant.partner_id_this_week', 'participant.finished',
     'participant.pay_game', 'participant.minimum_payoff_set', 'participant.minimum_payoff',
     'participant.public_payoff_set', 'participant.public_payoff', 'participant.week_payoff_set',
     'participant.week_payoff', 'participant.pay_week', 'participant.final_payoff', 'participant.is_finished',
     'participant.dictator_decision', 'participant.trust_decision', 'participant.public_decision',
     'participant.minimum_decision', 'session.code', 'session.label', 'session.config.real_world_currency_per_point',
     'session.config.participation_fee', 'session.config.week']


def get_partner(week_data, pd, game):
    for p in week_data:
        if p['participant.id_in_session'] == pd['participant.partner_id_this_week']:
            # partner found
            # check if they have finished, otherwise, search other partner
            if p['participant.is_finished'] == '1':
                # all good, can match
                return p

            else:
                # not good, need another partner
                # shuffle list of week data to get a randomly drawn other partner.
                week_data_copy = week_data.copy()
                random.shuffle(week_data_copy)
                for p_a in week_data_copy:
                    if p_a['participant.id_in_session'] not in [pd['participant.partner_id_this_week'], p['participant.id_in_session']] and p_a['participant.is_finished'] == '1':
                        if game == 'dictator':
                            if p_a['participant.dictator_this_week'] == '1':
                                return p_a
                        if game == 'trust':
                            pass
                        return p_a


def calculate_dictator_payoffs(week_data):
    partner_id = None
    my_payoff = 0.0
    partner_payoff = 0.0
    results = []
    for pd in week_data:
        my_id = pd['participant.id_in_session']
        if pd['participant.dictator_this_week'] == '1':
            my_payoff = DICTATOR_ENDOWMENT - float(pd['participant.dictator_decision'])
            partner_payoff = float(pd['participant.dictator_decision'])
        else:
            partner = get_partner(week_data, pd, 'dictator')
            my_payoff = float(partner['participant.dictator_decision'])
            partner_payoff = DICTATOR_ENDOWMENT - float(partner['participant.dictator_decision'])
            partner_id = partner['participant.id_in_session']

        results.append((my_id, my_payoff, partner_id, partner_payoff))
    return results


def calculate_public_payoffs(week_data):
    results = []
    for pd in week_data:
        my_id = pd['participant.id_in_session']
        myself = pd
        my_contribution = float(myself['participant.public_decision'])

        partner = get_partner(week_data, pd, 'public')
        partner_id = partner['participant.id_in_session']
        partner_contribution = float(partner['participant.public_decision'])

        public_good_pot = my_contribution + partner_contribution

        my_payoff = PUBLIC_ENDOWMENT - my_contribution + PUBLIC_MPCR * public_good_pot
        partner_payoff = PUBLIC_ENDOWMENT - partner_contribution + PUBLIC_MPCR * public_good_pot

        results.append((my_id, my_payoff, partner_id, partner_payoff))
    return results


def calculate_minimum_payoffs(week_data):
    results = []
    for pd in week_data:
        my_id = pd['participant.id_in_session']
        myself = pd

        partner = get_partner(week_data, pd, 'minimum')
        partner_id = partner['participant.id_in_session']

        my_number = int(myself['participant.minimum_decision'])
        others_number = int(partner['participant.minimum_decision'])

        if my_number >= others_number:
            my_payoff = MINIMUM_P1 * others_number + MINIMUM_P2 * (MINIMUM_MAX_NUMBER - my_number)
            others_payoff = MINIMUM_P1 * my_number + MINIMUM_P2 * (MINIMUM_MAX_NUMBER - others_number)
        else:
            my_payoff = MINIMUM_P1 * my_number + MINIMUM_P2 * (MINIMUM_MAX_NUMBER - others_number)
            others_payoff = MINIMUM_P1 * others_number + MINIMUM_P2 * (MINIMUM_MAX_NUMBER - my_number)

        results.append((my_id, my_payoff, partner_id, others_payoff))
    return results
# 
# def calculate_trust_payoff(player: Player):
#     part = player.participant
# 
#     if part.trust_payoff_set:
#         return
# 
#     myself = player.in_round(part.task_rounds['trust_game'])
#     other = _get_partner(player.subsession, part.partner_id_this_week, 'trust_game')
# 
#     if not all([myself.participant.is_finished, other.participant.is_finished]):
#         return
# 
#     if part.trust_sender_this_week:
#         p1, p2 = myself, other
#     else:
#         p1, p2 = other, myself
# 
#     p1_decision, p1_payoff, p2_decision, p2_payoff = _trust_game_payoff(p1, p2)
# 
#     p1.participant.trust_decision = p1_decision
#     p2.participant.trust_decision = p2_decision
# 
#     p1.participant.trust_payoff = p1_payoff
#     p2.participant.trust_payoff = p2_payoff
# 
#     p1.participant.trust_payoff_set = True
#     p2.participant.trust_payoff_set = True
# 
# 
# def _trust_game_payoff(p1, p2):
#     p1_sends = p1.trust_p1_sent
#     p2_receives = p1_sends * C.TRUST_MULTIPLIER
# 
#     if 0 <= p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10:
#         p2_sends_back = p2.trust_p2_sent_1
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 2:
#         p2_sends_back = p2.trust_p2_sent_2
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 2 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 3:
#         p2_sends_back = p2.trust_p2_sent_3
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 3 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 4:
#         p2_sends_back = p2.trust_p2_sent_4
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 4 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 5:
#         p2_sends_back = p2.trust_p2_sent_5
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 5 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 6:
#         p2_sends_back = p2.trust_p2_sent_6
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 6 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 7:
#         p2_sends_back = p2.trust_p2_sent_7
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 7 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 8:
#         p2_sends_back = p2.trust_p2_sent_8
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 8 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 9:
#         p2_sends_back = p2.trust_p2_sent_9
#     elif C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT / 10 * 9 < p2_receives <= C.TRUST_MULTIPLIER * C.TRUST_ENDOWMENT:
#         p2_sends_back = p2.trust_p2_sent_10
#     else:
#         p2_sends_back = 0
# 
#     p1_payoff = C.TRUST_ENDOWMENT - p1_sends + math.floor(p2_sends_back/100 * p2_receives)
#     p2_payoff = C.TRUST_ENDOWMENT + p2_receives - math.floor(p2_sends_back/100 * p2_receives)
# 
#     return p1_sends, p1_payoff, p2_sends_back, p2_payoff
# 
# 
