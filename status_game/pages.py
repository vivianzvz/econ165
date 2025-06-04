from otree.api import *
from .models import C, Group, Subsession, Player, set_pd_payoffs


class EmailEntry(Page):
    form_model = 'player'
    form_fields = ['ucsc_email']

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        import pandas as pd
        import os

        path = os.path.join(os.path.dirname(__file__), 'ses_survey.csv')
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        ses_lookup = df.set_index('email').to_dict(orient='index')

        email = self.player.ucsc_email.strip().lower() + '@ucsc.edu'
        self.player.ucsc_email = email  # optional: store full email

        ses_data = ses_lookup.get(email)
        if ses_data:
            self.player.participant.vars['ses_self_rung'] = ses_data.get('ses_self_rung', '')
            self.player.participant.vars['ses_family_rung'] = ses_data.get('ses_family_rung', '')



# ---------- TRUST GAME ----------
class TrustSend(Page):
    form_model = 'group'
    form_fields = ['sent_amount']

    def is_displayed(self):
        return self.round_number in [1, 4] and self.player.id_in_group == 1

    def vars_for_template(self):
        return {
            'ses_self_rung': self.participant.vars.get('ses_self_rung', 'N/A'),
            'other_ses_rung': self.player.other_player().participant.vars.get('ses_self_rung', 'N/A'),
        }



# class TrustWaitPage(WaitPage):
#     def is_displayed(self):
#         return self.round_number in [1, 2]
#
#     def body_text(self):
#         if self.player.id_in_group == 2:
#             return "You are Participant B (the receiver). Please wait while Participant A decides how much to send you."
#         else:
#             return "Please wait for the other participant."
class TrustWaitPage(Page):
    def is_displayed(self):
        return self.round_number in [1, 4] and self.player.id_in_group == 2

    def vars_for_template(self):
        return dict(
            is_receiver=True,
            endowment=C.ENDOWMENT,
            multiplier=C.MULTIPLIER,
        )

    template_name = 'status_and_behavior/TrustWaitWithInstructions.html'

class TrustWaitAfterSend(WaitPage):
    def is_displayed(self):
        return self.round_number in [1, 4]


class TrustReturn(Page):
    form_model = 'group'
    form_fields = ['sent_back_amount']

    def is_displayed(self):
        return self.round_number in [1, 4] and self.player.id_in_group == 2

    def before_next_page(self):
        sender = self.group.get_player_by_id(1)
        receiver = self.group.get_player_by_id(2)
        sender.payoff = C.ENDOWMENT - self.group.sent_amount + self.group.sent_back_amount
        receiver.payoff = self.group.sent_amount * C.MULTIPLIER - self.group.sent_back_amount

    def vars_for_template(self):
        sent = self.group.field_maybe_none('sent_amount')
        return {
            'tripled_amount': sent * C.MULTIPLIER if sent is not None else 'N/A',
            'ses_self_rung': self.participant.vars.get('ses_self_rung', 'N/A'),
            'other_ses_rung': self.player.other_player().participant.vars.get('ses_self_rung', 'N/A'),
        }



class WaitPageAfterTrust(WaitPage):
    def is_displayed(self):
        return self.round_number in [1, 4]

    def after_all_players_arrive(self):
        pass


# ---------- DICTATOR GAME ----------
class DictatorDecision(Page):
    form_model = 'group'
    form_fields = ['kept']

    def is_displayed(self):
        return self.round_number in [2, 5] and self.player.id_in_group == 1

    def before_next_page(self):
        dictator = self.group.get_player_by_id(1)
        recipient = self.group.get_player_by_id(2)
        dictator.payoff = self.group.kept
        recipient.payoff = C.ENDOWMENT - self.group.kept

    def vars_for_template(self):
        return {
            'ses_self_rung': self.participant.vars.get('ses_self_rung', 'N/A'),
            'other_ses_rung': self.player.other_player().participant.vars.get('ses_self_rung', 'N/A'),
        }


class DictatorWaitForDecision(Page):
    def is_displayed(self):
        return self.round_number in [2,5] and self.player.id_in_group == 2

    template_name = 'status_and_behavior/DictatorWaitWithInstructions.html'


# ---------- PRISONER'S DILEMMA ----------
class PDDecision(Page):
    form_model = 'player'
    form_fields = ['cooperate']

    def is_displayed(self):
        return self.round_number in [3, 6]

    def vars_for_template(self):
        return dict(
            pd_cc=C.PD_CC,
            pd_cd=C.PD_CD,
            pd_dc=C.PD_DC,
            pd_dd=C.PD_DD,
            ses_self_rung=self.participant.vars.get('ses_self_rung', 'N/A'),
            other_ses_rung=self.player.other_player().participant.vars.get('ses_self_rung', 'N/A'),
        )

    template_name = 'status_and_behavior/PDDecision.html'

class PDWaitPage(WaitPage):
    def is_displayed(self):
        return self.round_number in [3, 6]

    after_all_players_arrive = set_pd_payoffs


class WaitBeforeFinal(WaitPage):
    def is_displayed(self):
        return self.round_number in [3, 6]


# ---------- FINAL RESULTS ----------
class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS

    def vars_for_template(self):
        total_payoff = sum([p.payoff for p in self.player.in_all_rounds()])
        return dict(total_payoff=total_payoff)


# ---------- PAGE SEQUENCE ----------
page_sequence = [
    EmailEntry,
    TrustSend,               # P1 sends
    TrustWaitPage,
    TrustWaitAfterSend,      # P2 waits
    TrustReturn,             # P2 returns
    WaitPageAfterTrust,      # sync both players
    DictatorDecision,        # P1 makes Dictator decision
    DictatorWaitForDecision, # P2 waits, sees instructions
    PDDecision,              # PD part 1
    PDWaitPage,              # wait for next round of PD
    WaitBeforeFinal,         # optional sync before results
    FinalResults,
]
