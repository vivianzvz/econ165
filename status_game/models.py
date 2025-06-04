from otree.api import *
import pandas as pd
import os


doc = """
Unified experiment: Dictator, Trust, Prisoner’s Dilemma with and without SES info.
Rounds 1-2: Trust Game
Rounds 3-4: Dictator Game
Rounds 5-6: Prisoner's Dilemma
Even rounds show SES.
"""


class C(BaseConstants):
    NAME_IN_URL = 'status_and_behavior'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 6
    ENDOWMENT = cu(100)
    MULTIPLIER = 3  # for Trust Game
    # PD Payoffs
    PD_CC = cu(200)  # both cooperate
    PD_CD = cu(50)   # you cooperate, other defects
    PD_DC = cu(350)  # you defect, other cooperates
    PD_DD = cu(100)  # both defect



class Subsession(BaseSubsession):
    def creating_session(subsession):
        if subsession.round_number == 1:
            subsession.group_randomly(fixed_id_in_group=True)

            # Load SES data from CSV
            path = os.path.join(os.path.dirname(__file__), 'ses_survey.csv')
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            ses_lookup = df.set_index('email')['ses_self_rung'].to_dict()
            family_lookup = df.set_index('email')['ses_family_rung'].to_dict()

            # Assign SES info to participants
            for p in subsession.get_players():
                email = p.ucsc_email.strip().lower() if p.ucsc_email else ""
                p.participant.vars['ses_self_rung'] = ses_lookup.get(email, "Not available")
                p.participant.vars['ses_family_rung'] = family_lookup.get(email, "Not available")

        else:
            subsession.group_like_round(1)



class Group(BaseGroup):
    # Trust Game
    sent_amount = models.CurrencyField(min=0, max=C.ENDOWMENT, blank=True)
    sent_back_amount = models.CurrencyField(blank=True)

    # Dictator Game
    kept = models.CurrencyField(min=0, max=C.ENDOWMENT, blank=True)

    # # Prisoner's Dilemma
    # pd_choice_p1 = models.StringField(choices=['Cooperate', 'Defect'], blank=True)
    # pd_choice_p2 = models.StringField(choices=['Cooperate', 'Defect'], blank=True)


class Player(BasePlayer):
    ucsc_email = models.StringField(label="Enter your UCSC email (same as used in survey)")
    ses_self_rung = models.StringField(blank=True)
    ses_family_rung = models.StringField(blank=True)

    cooperate = models.BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        widget=widgets.RadioSelect,
        label="What do you choose?"
    )

    def other_player(self):
        return self.get_others_in_group()[0]

    def sees_ses(self):
        """Return True if SES info should be shown this round."""
        return self.round_number >= 4  # rounds 4, 5, 6 show SES
        # return self.round_number % 2 == 0 if even rounds show SES


# FUNCTIONS

def set_pd_payoffs(group: Group):
    p1, p2 = group.get_players()

    c1 = p1.field_maybe_none('cooperate')
    c2 = p2.field_maybe_none('cooperate')

    if c1 is None or c2 is None:
        return

    if c1 and c2:
        p1.payoff = C.PD_CC
        p2.payoff = C.PD_CC
    elif c1 and not c2:
        p1.payoff = C.PD_CD
        p2.payoff = C.PD_DC
    elif not c1 and c2:
        p1.payoff = C.PD_DC
        p2.payoff = C.PD_CD
    else:
        p1.payoff = C.PD_DD
        p2.payoff = C.PD_DD
