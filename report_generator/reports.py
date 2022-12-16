import csv
from pandas import ExcelFile
import win32com.client as win32
import math
import ast

from payments import *

EXCLUDES = [
    'participant._is_bot',
    'participant._index_in_pages',
    'participant._max_page_index',
    'participant._current_app_name',
    'participant._current_page_name',
    'participant.time_started_utc',
    'participant.mturk_worker_id',
    'participant.mturk_assignment_id',
    'session.mturk_HITId',
    'session.mturk_HITGroupId',
    'session.comment',
    'session.is_demo',
    'session.config.name'
]


def read_data_from_files():
    data = dict(week1=[], week2=[], week3=[], week4=[])
    for i in range(1, 5):
        with open(f'data/real/week{i}/all_apps_wide.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                data[f'week{i}'].append(row)
    return data


def get_participant_data(data_by_week, label, week):
    data = data_by_week[f"week{week}"]
    for row in data:
        if row['participant.label'] == label:
            return row


def get_data_by_week_id(week_data, partner_id):
    for row in week_data:
        if row['participant.id_in_session'] == partner_id:
            return row
    return {}


def aggregate_data_by_participant(data_by_week):
    participant_labels = [row['participant.label'] for row in data_by_week['week1']]

    data_by_participant = dict()
    for label in participant_labels:
        data_by_participant[label] = {
            'self': {
                'week1': get_participant_data(data_by_week, label=label, week=1),
                'week2': get_participant_data(data_by_week, label=label, week=2),
                'week3': get_participant_data(data_by_week, label=label, week=3),
                'week4': get_participant_data(data_by_week, label=label, week=4)
            },
            'partner': dict()
        }

    for label in data_by_participant.keys():
        for i in range(1, 5):
            d = data_by_participant[label]["self"][f"week{i}"]
            if d:
                partner_id = d['participant.partner_id_this_week']
                data_by_participant[label]["partner"][f"week{i}"] = get_data_by_week_id(data_by_week[f'week{i}'], partner_id)
            else:
                data_by_participant[label]["partner"][f"week{i}"] = {}

    return data_by_participant


# This function assumes that everyone participated in all four weeks and there are no missing values
# I need a fallback option in case there is no partner's data for that week.
def extract_report_data(data_by_participant, label, data_by_week):
    game_info = []
    game_info_dict = {}
    data = data_by_participant[label]
    week_to_pay = data["self"]['week1']['participant.pay_week']
    own_week_data = data["self"][f"week{week_to_pay}"]

    game_info.append(f"Für Sie wurde Woche {week_to_pay} zufällig zur Auszahlung ausgewählt.")

    game_to_pay = own_week_data['participant.pay_game']
    final_payoff = own_week_data['participant.final_payoff']

    game_info_dict['week_to_pay'] = week_to_pay
    game_info_dict['game_to_pay'] = game_to_pay
    game_info_dict['final_payoff'] = final_payoff

    if game_to_pay == 'dictator':
        
        partner_id = own_week_data['participant.dictator_partner_id_this_week']
        partner_week_data = get_data_by_week_id(data_by_week[f"week{week_to_pay}"], partner_id)
        game_info_dict['partner_id'] = partner_id
        
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation D zur Auszahlung bestimmt.")
        if own_week_data["participant.dictator_this_week"] == '1':
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler A.")
            decision = own_week_data['participant.dictator_decision']
            payoff = own_week_data['participant.dictator_payoff']
            game_info.append(f"Sie haben {decision} Punkte an den anderen Spieler abgegeben.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
            game_info_dict['role'] = 'dictator'
            game_info_dict['decision'] = decision
            game_info_dict['partner_decision'] = None
            game_info_dict['payoff'] = payoff
        else:
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler B.")
            payoff = own_week_data['participant.dictator_payoff']
            partner_decision = partner_week_data['participant.dictator_decision']
            game_info.append(f"Spieler A hat Ihnen {partner_decision} abgegeben.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
            
            game_info_dict['role'] = 'recipient'
            game_info_dict['decision'] = None
            game_info_dict['partner_decision'] = partner_decision
            game_info_dict['payoff'] = payoff

    elif game_to_pay == 'trust':
        partner_id = own_week_data['participant.trust_partner_id_this_week']
        partner_week_data = get_data_by_week_id(data_by_week[f"week{week_to_pay}"], partner_id)
        game_info_dict['partner_id'] = partner_id
        
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation T zur Auszahlung bestimmt.")
        if own_week_data["participant.trust_sender_this_week"] == '1':
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler A.")
            decision = own_week_data['participant.trust_decision']
            payoff = own_week_data['participant.trust_payoff']
            game_info.append(f"Sie haben {decision} Punkte an den anderen Spieler gesendet.")
            partner_decision = partner_week_data['participant.trust_decision']
            game_info.append(f"Spieler B hat Ihnen {partner_decision} Prozent der verdreifachten Punkte zurückgesendet.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
            game_info_dict['role'] = 'p1'
            game_info_dict['decision'] = decision
            game_info_dict['partner_decision'] = partner_decision
            game_info_dict['payoff'] = payoff
        else:
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler B.")
            decision = own_week_data['participant.trust_decision']
            payoff = own_week_data['participant.trust_payoff']
            partner_decision = partner_week_data['participant.trust_decision']
            game_info.append(f"Spieler A hat Ihnen {partner_decision} Punkte gesendet, die verdreifacht wurden.")
            game_info.append(f"Sie haben {decision} Prozent der erhaltenen Punkte an Spieler A zurück gesendet.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
            game_info_dict['role'] = 'p2'
            game_info_dict['decision'] = decision
            game_info_dict['partner_decision'] = partner_decision
            game_info_dict['payoff'] = payoff

    elif game_to_pay == 'public':
        partner_id = own_week_data['participant.public_partner_id_this_week']
        partner_week_data = get_data_by_week_id(data_by_week[f"week{week_to_pay}"], partner_id)
        game_info_dict['partner_id'] = partner_id
        
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation P zur Auszahlung bestimmt.")
        decision = own_week_data['participant.public_decision']
        payoff = own_week_data['participant.public_payoff']
        
        game_info.append(f"Sie haben {decision} Punkte in den gemeinsamen Topf eingezahlt.")
        partner_decision = partner_week_data['participant.public_decision']
        game_info.append(f"Der andere Spieler hat {partner_decision} Punkte in den gemeinsamen Topf eingezahlt.")
        game_info.append("Die Summe im gemeinsamen Topf wurde zunächst mit 1,6 multipliziert und dann gleichmäßig auf beide Spieler aufgeteilt.")
        game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
        game_info_dict['role'] = None
        game_info_dict['decision'] = decision
        game_info_dict['partner_decision'] = partner_decision
        game_info_dict['payoff'] = payoff

    elif game_to_pay == 'minimum':
        partner_id = own_week_data['participant.minimum_partner_id_this_week']
        partner_week_data = get_data_by_week_id(data_by_week[f"week{week_to_pay}"], partner_id)
        game_info_dict['partner_id'] = partner_id
        
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation M zur Auszahlung bestimmt.")
        decision = own_week_data['participant.minimum_decision']
        payoff = own_week_data['participant.minimum_payoff']
        
        game_info.append(f"Sie haben die Zahl {decision} gewählt.")
        partner_decision = partner_week_data['participant.minimum_decision']
        game_info.append(f"Der andere Spieler hat die Zahl {partner_decision} gewählt.")
        game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
        game_info_dict['role'] = None
        game_info_dict['decision'] = decision
        game_info_dict['partner_decision'] = partner_decision
        game_info_dict['payoff'] = payoff

    else:
        raise Exception('game not found')

    game_info.append(f'Ihre Gesamtauszahlung (inkl. fixer Auszahlung) beträgt {final_payoff} EUR.')
    game_info_dict['final_payoff'] = final_payoff


    return game_info, game_info_dict


def get_recipient_data(filename):
    xls = ExcelFile(filename)
    return xls.parse(xls.sheet_names[0])


def save_email_messages(label, text, subject, recipient):
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = recipient
    mail.Subject = subject
    mail.Body = text
    mail.SaveAs(Path=f'C:\Output\{label}.msg')


def extract_contact_details(recipients, label):
    rec = recipients.loc[recipients['label'] == label]
    first = rec['Firstname'].item()
    last = rec['Lastname'].item()
    email = rec['Email'].item()
    return first, last, email

def build_and_save_emails(data_by_participant, recipients, data_by_week, success_template_file="templates/study_completed.txt", not_finished_template_file="templates/study_not_completed.txt"):
    with open(success_template_file, 'r', encoding='utf-8') as f:
        success_template = f.read()

    with open(not_finished_template_file, 'r', encoding='utf-8') as f:
        not_finished_template = f.read()

    game_info_list = list()

    for label, data in data_by_participant.items():
        first, last, email = extract_contact_details(recipients, label)
        if data['self']['study_completed']:
            game_info, game_info_dict = extract_report_data(data_by_participant, label, data_by_week)
            game_info_dict['first'] = first
            game_info_dict['last'] = last
            game_info_dict['email'] = email
            game_info_dict['iban'] = data['self']['week1']['questionnaires.1.player.iban'].replace(' ', '')
            game_info_list.append(game_info_dict)
            report = "\n".join(game_info)

            email_body = success_template
            email_body = email_body.replace("{{ firstname }}", first)
            email_body = email_body.replace("{{ lastname }}", last)
            email_body = email_body.replace("{{ game_report }}", report)

            save_email_messages(label, email_body, 'Online-Experiment: Ihre Auszahlungsübersicht', email)
        else:
            email_body = not_finished_template
            email_body = email_body.replace("{{ firstname }}", first)
            email_body = email_body.replace("{{ lastname }}", last)

            save_email_messages(label, email_body, 'Informationen zu Ihrer Teilnahme an unserem Online-Experiment', email)

    with open('report.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=game_info_list[0].keys())
        writer.writeheader()
        writer.writerows(game_info_list)

    # prepare batch payment
    wise_data = []
    for g in game_info_list:
        d = {
            'name': f"{g['first']} {g['last']}",
            'recipientEmail': g['email'],
            'paymentReference': 'Auszahlung',
            'receiverType': 'PERSON',
            'amountCurrency': 'source',
            'amount': g['final_payoff'],
            'sourceCurrency': 'EUR',
            'targetCurrency': 'EUR',
            'IBAN': g['iban']
        }
        wise_data.append(d)

    with open('wise.csv', 'w', encoding='utf-8', newline='') as f:
        writer2 = csv.DictWriter(f, fieldnames=wise_data[0].keys())
        writer2.writeheader()
        writer2.writerows(wise_data)

def participant_data_only(data_by_week):
    filtered_data = dict()
    for i in range(1, 5):
        filtered_week_data = list()
        for row in data_by_week[f'week{i}']:
            filtered_row_data = dict()
            for key, value in row.items():
                if (key.startswith('participant.') or key.startswith('session.') or key == 'questionnaires.1.player.iban') and key not in EXCLUDES:
                    filtered_row_data[key] = value
            filtered_week_data.append(filtered_row_data)
        filtered_data[f'week{i}'] = filtered_week_data
    return filtered_data


def get_finished_only(data_by_week):
    filtered_data = dict()
    for i in range(1, 5):
        filtered_week_data = list()
        for row in data_by_week[f'week{i}']:
            if row['participant.is_finished'] == '0':
                continue
            filtered_week_data.append(row)
        filtered_data[f'week{i}'] = filtered_week_data
    return filtered_data

def fix_decisions(data_by_week):
    result = dict()
    for i in range(1, 5):
        week_data = data_by_week[f'week{i}']
        for row in week_data:
            
            if any([row['participant.minimum_payoff'] == '', row['participant.trust_payoff'] == '', row['participant.dictator_payoff'] == '', row['participant.public_payoff'] == '']):
                task_rounds = ast.literal_eval(row['participant.task_rounds'])
                row['participant.minimum_decision'] = row[f'games.{task_rounds["minimum_effort"]}.player.minimum_number_selected']
                row['participant.public_decision'] = row[f'games.{task_rounds["public_good"]}.player.public_contribution']
                
                # role specific!
                if row['participant.dictator_this_week'] == '1':
                    row['participant.dictator_decision'] = row[f'games.{task_rounds["dictator"]}.player.dictator_amount_sent']
                else:
                    row['participant.dictator_decision'] = ''
    
                if row['participant.trust_sender_this_week'] == '1':
                    row['participant.trust_decision'] = row[f'games.{task_rounds["trust_game"]}.player.trust_p1_sent']
                else:
                    row['participant.trust_decision'] = '0'
                    
        result[f'week{i}'] = week_data
    return result


def main():
    # data from experiments
    data_by_week = read_data_from_files()

    finished_by_week = get_finished_only(data_by_week)
    # fix decisions
    fixed_by_week = fix_decisions(finished_by_week)
    


    # filter for necessary data
    selected_data_by_week = participant_data_only(fixed_by_week)


    # print(calculate_dictator_payoffs(selected_data_by_week['week1']))

    # manipulate test data to have a known unfinished participant
    # selected_data_by_week['week1'][0]['participant.is_finished'] = '0'
    # selected_data_by_week['week1'][4]['participant.is_finished'] = '0'
    # print(calculate_dictator_payoffs(selected_data_by_week['week1']))
    # print(calculate_public_payoffs(selected_data_by_week['week1']))
    # print(calculate_minimum_payoffs(selected_data_by_week['week1']))
    # print(calculate_trust_payoffs(selected_data_by_week['week1']))
    
    for i in range(1, 5):
        week_data = selected_data_by_week[f'week{i}']
        
        # calc payoffs
        dg = calculate_dictator_payoffs(week_data)
        pu = calculate_public_payoffs(week_data)
        mi = calculate_minimum_payoffs(week_data)
        tg = calculate_trust_payoffs(week_data)

        for p_data in week_data:
            for j in range(0, len(dg)):
                # dictator
                if p_data['participant.id_in_session'] == dg[j][0]:
                    p_data['participant.dictator_payoff'] = dg[j][1]
                    if p_data['participant.partner_id_this_week'] is not None:
                        p_data['participant.dictator_partner_id_this_week'] = dg[j][2]
                    if p_data['participant.pay_game'] == 'dictator':
                        p_data['participant.week_payoff'] = p_data['participant.dictator_payoff']
                    if p_data['participant.pay_week'] == f'{i}' and p_data['participant.week_payoff']:
                        p_data['participant.final_payoff'] = round(float(p_data['participant.week_payoff']) / 10 + 4, 2)

            for j in range(0, len(tg)):
                # trust
                if p_data['participant.id_in_session'] == tg[j][0]:
                    p_data['participant.trust_payoff'] = tg[j][1]
                    p_data['participant.trust_partner_id_this_week'] = tg[j][2]

                    if p_data['participant.pay_game'] == 'trust':
                        p_data['participant.week_payoff'] = p_data['participant.trust_payoff']
                    if p_data['participant.pay_week'] == f'{i}' and p_data['participant.week_payoff']: 
                        p_data['participant.final_payoff'] = round(float(p_data['participant.week_payoff']) / 10 + 4, 2) 
    
            for j in range(0, len(pu)):
                # public
                if p_data['participant.id_in_session'] == pu[j][0]:
                    p_data['participant.public_payoff'] = pu[j][1]
                    p_data['participant.public_partner_id_this_week'] = pu[j][2]
                    
                    if p_data['participant.pay_game'] == 'public':
                        p_data['participant.week_payoff'] = p_data['participant.public_payoff']
                    if p_data['participant.pay_week'] == f'{i}' and p_data['participant.week_payoff']:
                        p_data['participant.final_payoff'] = round(float(p_data['participant.week_payoff']) / 10 + 4, 2) 
                        
            for j in range(0, len(mi)):
                # minimum
                if p_data['participant.id_in_session'] == mi[j][0]:
                    p_data['participant.minimum_payoff'] = mi[j][1]
                    p_data['participant.minimum_partner_id_this_week'] = mi[j][2]

                if p_data['participant.pay_game'] == 'minimum':
                    p_data['participant.week_payoff'] = p_data['participant.minimum_payoff']
                if p_data['participant.pay_week'] == f'{i}' and p_data['participant.week_payoff']:
                    p_data['participant.final_payoff'] = round(float(p_data['participant.week_payoff']) / 10 + 4, 2) 
    # data by participants
    data_by_participant = aggregate_data_by_participant(selected_data_by_week)
    

    for label in data_by_participant.keys():
        # check if they completed all weeks
        weekly_is_finished = [data_by_participant[label]['self'][f'week{i}']['participant.is_finished'] for i in range(1, 5) if data_by_participant[label]['self'][f'week{i}'] is not None]
        if len(weekly_is_finished) < 4:
            data_by_participant[label]['self']['study_completed'] = False
        else:
            data_by_participant[label]['self']['study_completed'] = all(weekly_is_finished)

    # recipients from hroot
    all_recipients = get_recipient_data('data/Recipients.xlsx')
    df = all_recipients.loc[:49]  # get 50 first entries, because other entries are duplicates (secondary emails)


    # # email preparation
    build_and_save_emails(data_by_participant, df, selected_data_by_week)


if __name__ == '__main__':
    main()
