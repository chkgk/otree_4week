import csv
from pandas import ExcelFile
import win32com.client as win32


def read_data_from_files():
    data = dict(week1=[], week2=[], week3=[], week4=[])
    for i in range(1, 5):
        with open(f'data/week{i}/all_apps_wide.csv', 'r') as f:
            reader = csv.DictReader(f)
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
            partner_id = d['participant.partner_id_this_week']
            data_by_participant[label]["partner"][f"week{i}"] = get_data_by_week_id(data_by_week[f'week{i}'], partner_id)

    return data_by_participant


def extract_report_data(data_by_participant, label):
    game_info = []
    data = data_by_participant[label]
    week_to_pay = data["self"]['week1']['participant.pay_week']
    own_week_data = data["self"][f"week{week_to_pay}"]
    partner_week_data = data["partner"][f"week{week_to_pay}"]
    game_info.append(f"Für Sie wurde Woche {week_to_pay} zufällig zur Auszahlung ausgewählt.")

    game_to_pay = own_week_data['participant.pay_game']
    final_payoff = own_week_data['participant.final_payoff']

    if game_to_pay == 'dictator':
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation D zur Auszahlung bestimmt.")
        if own_week_data["participant.dictator_this_week"] == '1':
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler A.")
            decision = own_week_data['participant.dictator_decision']
            payoff = own_week_data['participant.dictator_payoff']
            game_info.append(f"Sie haben {decision} Punkte an den anderen Spieler abgegeben.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
        else:
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler B.")
            payoff = own_week_data['participant.dictator_payoff']
            partner_decision = partner_week_data['participant.dictator_decision']
            game_info.append(f"Spieler A hat Ihnen {partner_decision} abgegeben.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")

    elif game_to_pay == 'trust':
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation T zur Auszahlung bestimmt.")
        if own_week_data["participant.trust_sender_this_week"] == '1':
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler A.")
            decision = own_week_data['participant.trust_decision']
            payoff = own_week_data['participant.trust_payoff']
            game_info.append(f"Sie haben {decision} Punkte an den anderen Spieler gesendet.")
            partner_decision = partner_week_data['participant.trust_decision']
            game_info.append(f"Spieler B hat Ihnen {partner_decision} Prozent der verdreifachten Punkte zurückgesendet.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")
        else:
            game_info.append("In dieser Situation waren Sie in der Rolle von Spieler B.")
            decision = own_week_data['participant.trust_decision']
            payoff = own_week_data['participant.trust_payoff']
            partner_decision = partner_week_data['participant.trust_decision']
            game_info.append(f"Spieler A hat Ihnen {partner_decision} Punkte gesendet, die verdreifacht wurden.")
            game_info.append(f"Sie haben {decision} Prozent der erhaltenen Punkte an Spieler A zurück gesendet.")
            game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")

    elif game_to_pay == 'public':
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation P zur Auszahlung bestimmt.")
        decision = own_week_data['participant.public_decision']
        payoff = own_week_data['participant.public_payoff']
        game_info.append(f"Sie haben {decision} Punkte in den gemeinsamen Topf eingezahlt.")
        partner_decision = partner_week_data['participant.public_decision']
        game_info.append(f"Der andere Spieler hat {partner_decision} Punkte in den gemeinsamen Topf eingezahlt.")
        game_info.append("Die Summe im gemeinsamen Topf wurde zunächst mit 1,6 multipliziert und dann gleichmäßig auf beide Spieler aufgeteilt.")
        game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")

    elif game_to_pay == 'minimum':
        game_info.append("Ein weiterer Zufallszug hat Entscheidungssituation M zur Auszahlung bestimmt.")
        decision = own_week_data['participant.minimum_decision']
        payoff = own_week_data['participant.minimum_payoff']
        game_info.append(f"Sie haben die Zahl {decision} gewählt.")
        partner_decision = partner_week_data['participant.minimum_decision']
        game_info.append(f"Der andere Spieler hat die Zahl {partner_decision} gewählt.")
        game_info.append(f"Ihre Auszahlung in dieser Entscheidungssituation beträgt daher {payoff} Punkte.")

    else:
        raise Exception('game not found')

    game_info.append(f'Ihre Gesamtauszahlung (inkl. fixer Auszahlung) beträgt {final_payoff} EUR.')

    # print(own_week_data)
    # print(partner_week_data)

    return game_info


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


def build_and_save_emails(data_by_participant, recipients, template_file="templates/report_template.txt"):
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()

    for label, data in data_by_participant.items():
        game_info = extract_report_data(data_by_participant, label)
        rec = recipients.loc[recipients['label'] == label]
        first = rec['Firstname'].item()
        last = rec['Lastname'].item()
        email = rec['Email'].item()
        report = "\n".join(game_info)

        email_body = template
        email_body = email_body.replace("{{ firstname }}", first)
        email_body = email_body.replace("{{ lastname }}", last)
        email_body = email_body.replace("{{ game_report }}",report)

        save_email_messages(label, email_body, 'Online-Experiment: Ihre Auszahlungsübersicht', email)


def main():
    # data from experiments
    data_by_week = read_data_from_files()
    data_by_participant = aggregate_data_by_participant(data_by_week)

    # recipients from hroot
    all_recipients = get_recipient_data('data/Recipients.xlsx')
    df = all_recipients.loc[:49]  # get 50 first entries, because other entries are duplicates (secondary emails)

    # email preparation
    build_and_save_emails(data_by_participant, df)


if __name__ == '__main__':
    main()
