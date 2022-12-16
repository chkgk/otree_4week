import random
import math

DICTATOR_ENDOWMENT = 200
PUBLIC_ENDOWMENT = 100
PUBLIC_MPCR = 0.8

MINIMUM_MAX_NUMBER = 100
MINIMUM_P1 = 1
MINIMUM_P2 = 0.5

TRUST_ENDOWMENT = (100)
TRUST_MULTIPLIER = 3

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

TRUST_ENDOWMENT = 100
TRUST_MULTIPLIER = 3


def _trust_game_payoff(p1_decision, p2_decision):
    p1_sends = p1_decision
    p2_receives = p1_decision * TRUST_MULTIPLIER
    p2_sends_back = p2_decision

    p1_payoff = TRUST_ENDOWMENT - p1_sends + math.floor(p2_sends_back/100 * p2_receives)
    p2_payoff = TRUST_ENDOWMENT + p2_receives - math.floor(p2_sends_back/100 * p2_receives)

    return p1_sends, p1_payoff, p2_sends_back, p2_payoff


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
                        if p_a['participant.trust_sender_this_week'] == '1':
                            return p_a

                    if game == 'public' or game == 'minimum':
                        return p_a



def calculate_dictator_payoffs(week_data):
    partner_id = None
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


def calculate_trust_payoffs(week_data):
    partner_id = None
    results = []
    for tg in week_data:
        # print(tg)
        my_id = tg['participant.id_in_session']
        partner = get_partner(week_data, tg, 'trust')
        partner_id = partner['participant.id_in_session']
        if tg['participant.trust_sender_this_week'] == '1':
            p1, p2 = tg, partner
            p1_decision = float(tg['participant.trust_decision'])
            p2_decision = float(partner['participant.trust_decision'])

            p1_sends, p1_payoff, p2_sends_back, p2_payoff = _trust_game_payoff(p1_decision, p2_decision)
            my_payoff, partner_payoff = p1_payoff, p2_payoff

        else:
            p1, p2 = partner, tg
            p1_decision = float(partner['participant.trust_decision'])
            p2_decision = float(tg['participant.trust_decision'])

            p1_sends, p1_payoff, p2_sends_back, p2_payoff = _trust_game_payoff(p1_decision, p2_decision)
            my_payoff, partner_payoff = p2_payoff, p1_payoff

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

