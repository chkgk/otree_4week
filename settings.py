from os import environ

SESSION_CONFIGS = [
    dict(
        display_name="1a. Individual Lab Task - Session 1",
        name='instructions_lab_1',
        app_sequence=['instructions_lab'],
        num_demo_participants=12,
        labels="_rooms/pilot1.txt"
    ),
    dict(
        display_name="1b. Individual Lab Task - Session 2",
        name='instructions_lab_2',
        app_sequence=['instructions_lab'],
        num_demo_participants=12,
        labels="_rooms/pilot2.txt"
    ),
    dict(
        display_name="2. Group Lab Task",
        name='group_task',
        app_sequence=['group_task'],
        num_demo_participants=4,
    ),
    dict(
        display_name="3a. Online Task - Session 1",
        name='games_lab_1',
        app_sequence=['games_lab', 'questionnaires_lab'],
        num_demo_participants=12,
        labels="_rooms/pilot1.txt"
    ),
    dict(
        display_name="3b. Online Task - Session 2",
        name='games_lab_2',
        app_sequence=['games_lab', 'questionnaires_lab'],
        num_demo_participants=12,
        labels="_rooms/pilot2.txt"
    )
    # dict(
    #     name='questionnaires_lab',
    #     app_sequence=['questionnaires_lab'],
    #     num_demo_participants=4,
    # ),
    # dict(
    #     name='Week1',
    #     app_sequence=['instructions', 'games', 'questionnaires'],
    #     num_demo_participants=4,
    #     week=1
    # ),
    # dict(
    #     name='Week2',
    #     app_sequence=['instructions', 'games', 'questionnaires'],
    #     num_demo_participants=4,
    #     week=2
    # ),
    # dict(
    #     name='Week3',
    #     app_sequence=['instructions', 'games', 'questionnaires'],
    #     num_demo_participants=4,
    #     week=3
    # ),
    # dict(
    #     name='Week4',
    #     app_sequence=['instructions', 'games', 'questionnaires'],
    #     num_demo_participants=4,
    #     week=4
    # ),
    # dict(
    #     name='instructions_week1',
    #     app_sequence=['instructions'],
    #     num_demo_participants=4,
    #     week=1
    # ),
    # dict(
    #     name='instructions_week2',
    #     app_sequence=['instructions'],
    #     num_demo_participants=4,
    #     week=2
    # ),
    # dict(
    #     name='questionnaires_week1',
    #     app_sequence=['questionnaires'],
    #     num_demo_participants=4,
    #     week=1
    # ),
    # dict(
    #     name='questionnaires_week4',
    #     app_sequence=['questionnaires'],
    #     num_demo_participants=4,
    #     week=4
    # ),
    # dict(
    #     name='games_week1',
    #     app_sequence=['games'],
    #     num_demo_participants=4,
    #     week=1
    # )
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.10, participation_fee=8.00, doc=""
)

PARTICIPANT_FIELDS = [
    'task_rounds',
    'dictator_1',
    'dictator_2',
    'dictator_3',
    'dictator_4',
    'dictator_this_week',
    'dictator_payoff_set',
    'dictator_payoff',
    'trust_sender_1',
    'trust_sender_2',
    'trust_sender_3',
    'trust_sender_4',
    'trust_sender_this_week',
    'trust_payoff_set',
    'trust_payoff',
    'partner_id_1',
    'partner_id_2',
    'partner_id_3',
    'partner_id_4',
    'partner_id_this_week',
    'finished',
    'pay_game',
    'minimum_payoff_set',
    'minimum_payoff',
    'public_payoff_set',
    'public_payoff',
    'week_payoff_set',
    'week_payoff',
    'pay_week',
    'final_payoff',
    'is_finished',
    'dictator_decision',
    'trust_decision',
    'public_decision',
    'minimum_decision',
    'pos_in_group'
]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'de'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '6185353070723'

ROOMS = [
    # dict(
    #     name='4week',
    #     display_name='Main Experiment Room',
    #     participant_label_file='_rooms/4week.txt',
    #     use_secure_urls=True
    # ),
    # dict(
    #     name='4week_demo',
    #     display_name='DEMO Room',
    #     participant_label_file='_rooms/4week_demo.txt',
    #     use_secure_urls=True
    # ),
    dict(
        name='pilot_1',
        display_name='Pilot 1 - Online',
        participant_label_file='_rooms/pilot1.txt',
        use_secure_urls=True
    ),
    dict(
        name='pilot_2',
        display_name='Pilot 2 - Online',
        participant_label_file='_rooms/pilot2.txt',
        use_secure_urls=True
    ),
    dict(
        name='lab_pilot',
        display_name='Pilot - Lab'
    ),
    dict(
        name='lab_group',
        display_name='Pilot - Group'
    )
]

# DEBUG=False