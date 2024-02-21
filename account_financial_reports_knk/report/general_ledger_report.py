# -*- coding: utf-8 -*-

from odoo.tools import date_utils, get_lang
from dateutil.relativedelta import relativedelta
from babel.dates import get_quarter_names
from odoo.tools.misc import format_date

from odoo import api, fields, models


class ReportGeneralLedger(models.AbstractModel):
    _name = 'report.account_financial_reports_knk.report_general_ledger'
    _description = 'General Ledger'

    @api.model
    def _get_report_values(self, docids, data=None):
        dates = data.get('dates', 'this_month')
        entry_type = data.get('entry_type', 'all')
        journal_id = data.get('journal_id', '0')
        company_id = data.get('company_id', '0')
        prev_period = data.get('prev_period', '0')
        last_period = data.get('last_period', '0')
        datas = self._get_report_vals(dates, entry_type, journal_id, company_id, prev_period, last_period)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': [datas],
        }

    def _get_report_vals(self, dates, entry_type, journal_id, company_id, prev_period, last_period):
        move_lines = []
        domain = []
        compare_period = []
        if journal_id and journal_id not in ['0', 'undefined']:
            domain += [('move_id.journal_id', '=', int(journal_id))]
        if company_id and company_id not in ['0', 'undefined']:
            domain += [('move_id.company_id', '=', int(company_id))]
        if entry_type == 'all':
            domain += [('move_id.state', 'in', ['draft', 'posted'])]
        elif entry_type == 'draft':
            domain += [('move_id.state', '=', 'draft')]
        elif entry_type == 'posted':
            domain += [('move_id.state', '=', 'posted')]
        date_from, date_to = date_utils.get_month(fields.Date.context_today(self))
        string = format_date(self.env, fields.Date.to_string(date_to), date_format='MMM YYYY')
        quarter_names = get_quarter_names('abbreviated', locale=get_lang(self.env).code)
        if dates == 'this_month':
            string = format_date(self.env, fields.Date.to_string(date_to), date_format='MMM YYYY')
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        elif dates == 'this_quarter':
            date_from, date_to = date_utils.get_quarter(fields.Date.context_today(self))
            string = u'%s\N{NO-BREAK SPACE}%s' % (
                    quarter_names[date_utils.get_quarter_number(date_to)], date_to.year)
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        elif dates == 'this_fin_year':
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Date.context_today(self))
            date_from = company_fiscalyear_dates['date_from']
            date_to = company_fiscalyear_dates['date_to']
            string = date_to.strftime('%Y')
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        elif dates == 'last_month':
            date_from, date_to = date_utils.get_month(fields.Date.context_today(self))
            date_from = date_from - relativedelta(months=1)
            date_to = date_to - relativedelta(months=1)
            string = format_date(self.env, fields.Date.to_string(date_to), date_format='MMM YYYY')
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        elif dates == 'last_quarter':
            date_from, date_to = date_utils.get_quarter(fields.Date.context_today(self))
            date_from = date_from - relativedelta(months=1)
            date_from, date_to = date_utils.get_quarter(date_from)
            string = u'%s\N{NO-BREAK SPACE}%s' % (
                    quarter_names[date_utils.get_quarter_number(date_to)], date_to.year)
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        elif dates == 'last_fin_year':
            company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Date.context_today(self))
            date_from = company_fiscalyear_dates['date_from']
            date_to = company_fiscalyear_dates['date_to']
            date_from = date_from - relativedelta(years=1)
            date_to = date_to - relativedelta(years=1)
            string = date_to.strftime('%Y')
            domain += [('date', '>=', date_from), ('date', '<=', date_to)]
        line_data = self.env['account.move.line'].read_group(domain, ['account_id', 'debit', 'credit', 'date', 'partner_id', 'amount_currency', 'move_name'], ['account_id'])
        for ln in line_data:
            account = self.env['account.account'].browse(ln['account_id'][0])
            lines = self.env['account.move.line'].search(domain+[('account_id', '=', ln['account_id'][0])])
            partner = self.env['res.partner']
            if 'partner_id' in ln:
                partner = self.env['res.partner'].browse(ln['partner_id'][0])
            vals = {
                    'name': ln.get('move_name', ''),
                    'account': account.display_name,
                    'debit': ln['debit'],
                    'credit': ln['credit'],
                    'amount_currency': ln.get('amount_currency', 0.0),
                    'date': ln['date'],
                    'partner': partner.display_name,
                    'lines': lines,
                    'account_id': ln['account_id'][0]
                }
            move_lines.append(vals)
        currency_id = self.env.company.currency_id
        return {
            'move_lines': move_lines,
            'string': string,
            'currency_id': currency_id,
            'compare_period': compare_period,
        }

    @api.model
    def get_html(self, dates='this_month', entry_type='all', journal_id=False, company_id=False, prev_period=False, last_period=False):
        res = self._get_report_data()
        res['lines']['report_type'] = 'html'
        vals = self._get_report_vals(dates, entry_type, journal_id, company_id, prev_period, last_period)
        # res['lines'] = self.env.ref('account_financial_reports_knk.report_general_ledger_document')._render({'data': vals})
        res['lines'] = self.env['ir.ui.view']._render_template('account_financial_reports_knk.report_general_ledger_document', {'data': vals})
        res['selected_date_gl'] = vals['string']
        return res

    @api.model
    def _get_report_data(self):
        lines = {}
        journals = {}
        companies = {}
        for journal in self.env['account.journal'].search([]):
            journals[journal.id] = journal.display_name
        for company in self.env['res.company'].search([]):
            companies[company.id] = company.display_name
        return {
            'lines': lines,
            'journals': journals,
            'companies': companies,
            'report_name': 'general_ledger_report'
        }

    def account_move_print_xls_report(self, **args):
        ctx = self.env.context
        vals = self._get_report_vals(dates=ctx.get('dates'), entry_type=ctx.get('entry_type'), journal_id=ctx.get('journal_id'), company_id=ctx.get('company_id'), prev_period=ctx.get('prev_period'), last_period=ctx.get('last_period'))
        return vals
