from os import environ

SESSION_CONFIGS = [
    dict(
        name='boycott_game',
        display_name="Monopoly Boycott Game",
        app_sequence=['boycott_game'],
        num_demo_participants=12,
        demand_slope='step',
        use_chat=True,
    ),
    dict(
        name='ses_behavior',
        app_sequence=[
            'ses_survey',
            'dictator',
            'trust',
            'prisoner',
            'dictator_SES',
            'trust_SES',
            'prisoner_SES',
            'final_results',
        ],
        num_demo_participants=2,
    ),
    dict(
        name='boycott_project',
        display_name="Boycott Project",
        num_demo_participants=2,
        app_sequence=['block1_effort_wage', 'block2_market'],
    ),
]




SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01, participation_fee=5.00, doc=""
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='label',
        display_name='with labels',
        participant_label_file='_rooms_labeled.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo'),
]

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = "Here are some oTree games."
SECRET_KEY = '1554698864068'
INSTALLED_APPS = ['otree']
DEBUG = False
