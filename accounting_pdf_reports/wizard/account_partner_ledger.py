# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPartnerLedger(models.TransientModel):
    _name = "account.report.partner.ledger"
    _inherit = "account.common.partner.report"
    _description = "Account Partner Ledger"

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on "
                                          "report if the currency differs from "
                                          "the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')

    partner_ids = fields.Many2many('res.partner', 'partner_ledger_partner_rel',
                                   'id', 'partner_id', string='Partners')

    include_initial_balance = fields.Boolean(string='Include Initial Balance')





    def _get_report_data(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled,
                             'partner_ids': self.partner_ids.ids,
                             'initial_balance': self.include_initial_balance,
                             'amount_currency': self.amount_currency})
        return data

    def _print_report(self, data):
        data = self._get_report_data(data)
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').with_context(landscape=True).\
            report_action(self, data=data)
