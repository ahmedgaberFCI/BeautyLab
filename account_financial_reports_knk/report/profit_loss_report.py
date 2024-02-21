# -*- coding: utf-8 -*-

from odoo.tools import date_utils, get_lang
from dateutil.relativedelta import relativedelta
from babel.dates import get_quarter_names
from odoo.tools.misc import format_date

from odoo import api, fields, models


class ReportProfitLoss(models.AbstractModel):
    _name = 'report.account_financial_reports_knk.report_profit_loss'
    _description = 'Profit Loss Report'

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

    def _get_domain(self, account, dates, entry_type, journal_id, company_id):
        domain = [('account_id', '=', account.id)]
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
        return domain

    def _get_period_data(self, account, dates, entry_type, journal_id, company_id, prev_period, last_period):
        compare_period = []
        compare_period_names = []
        date_from, date_to = date_utils.get_month(fields.Date.context_today(self))
        last_date_from = date_from - relativedelta(months=1)
        string = format_date(self.env, fields.Date.to_string(date_to), date_format='MMM YYYY')
        quarter_names = get_quarter_names('abbreviated', locale=get_lang(self.env).code)
        curr_qt_date_from, curr_qt_date_to = date_utils.get_quarter(fields.Date.context_today(self))
        last_qt_date_from, last_qt_date_to = date_utils.get_quarter(curr_qt_date_from - relativedelta(months=1))
        company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fields.Date.context_today(self))
        curr_fis_from = company_fiscalyear_dates['date_from']
        last_fis_from = curr_fis_from - relativedelta(years=1)
        if last_period and last_period != '0':
            last_period = int(last_period)
            while last_period > 0:
                inital_balance = {'debit': 0.0, 'credit': 0.0}
                if dates is None or dates == 'this_month':
                    dt_from = date_from - relativedelta(years=last_period)
                    dt_to = date_to - relativedelta(years=last_period)
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = format_date(self.env, fields.Date.to_string(dt_to), date_format='MMM YYYY')
                    compare_period_names.append({'name': string})
                elif dates == 'this_quarter':
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    dt_from, dt_to = date_utils.get_quarter(curr_qt_date_from - relativedelta(years=last_period))
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = u'%s\N{NO-BREAK SPACE}%s' % (
                        quarter_names[date_utils.get_quarter_number(dt_to)], dt_to.year)
                    compare_period_names.append({'name': string})
                elif dates == 'this_fin_year':
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    fis_from = curr_fis_from - relativedelta(years=last_period)
                    company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fis_from)
                    dt_from = company_fiscalyear_dates['date_from']
                    dt_to = company_fiscalyear_dates['date_to']
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = dt_to.strftime('%Y')
                    compare_period_names.append({'name': string})
                elif dates == 'last_month':
                    dt_from, dt_to = date_utils.get_month(last_date_from - relativedelta(years=last_period))
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = format_date(self.env, fields.Date.to_string(dt_to), date_format='MMM YYYY')
                    compare_period_names.append({'name': string})
                elif dates == 'last_quarter':
                    dt_from = date_from - relativedelta(years=last_period)
                    dt_to = date_to - relativedelta(years=last_period)
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = u'%s\N{NO-BREAK SPACE}%s' % (
                        quarter_names[date_utils.get_quarter_number(dt_to)], dt_to.year)
                    compare_period_names.append({'name': string})
                elif dates == 'last_fin_year':
                    company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(last_fis_from)
                    date_from = company_fiscalyear_dates['date_from']
                    date_to = company_fiscalyear_dates['date_to']
                    dt_from = date_from - relativedelta(years=last_period)
                    dt_to = date_to - relativedelta(years=last_period)
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = dt_to.strftime('%Y')
                    compare_period_names.append({'name': string})
                line_data = self.env['account.move.line'].read_group(domain, ['account_id', 'debit', 'credit'], ['account_id'])
                for ln in line_data:
                    inital_balance['debit'] += ln['debit']
                    inital_balance['credit'] += ln['credit']
                compare_period.append(inital_balance)
                last_period -= 1
        elif prev_period:
            prev_period = int(prev_period)
            while prev_period > 0:
                inital_balance = {'debit': 0.0, 'credit': 0.0}
                if dates is None or dates == 'this_month' or dates == 'undefined':
                    dt_from, dt_to = date_utils.get_month(date_from - relativedelta(months=prev_period))
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = format_date(self.env, fields.Date.to_string(dt_to), date_format='MMM YYYY')
                    compare_period_names.append({'name': string})
                elif dates == 'this_quarter':
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    dt_from, dt_to = date_utils.get_quarter(curr_qt_date_from - relativedelta(months=prev_period*3))
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = u'%s\N{NO-BREAK SPACE}%s' % (
                        quarter_names[date_utils.get_quarter_number(dt_to)], dt_to.year)
                    compare_period_names.append({'name': string})
                elif dates == 'this_fin_year':
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    fis_from = curr_fis_from - relativedelta(years=prev_period)
                    company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(fis_from)
                    dt_from = company_fiscalyear_dates['date_from']
                    dt_to = company_fiscalyear_dates['date_to']
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = dt_to.strftime('%Y')
                    compare_period_names.append({'name': string})
                elif dates == 'last_month':
                    dt_from, dt_to = date_utils.get_month(last_date_from - relativedelta(months=prev_period))
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = format_date(self.env, fields.Date.to_string(dt_to), date_format='MMM YYYY')
                    compare_period_names.append({'name': string})
                elif dates == 'last_quarter':
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    dt_from, dt_to = date_utils.get_quarter(last_qt_date_from - relativedelta(months=prev_period*3))
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = u'%s\N{NO-BREAK SPACE}%s' % (
                        quarter_names[date_utils.get_quarter_number(dt_to)], dt_to.year)
                    compare_period_names.append({'name': string})
                elif dates == 'last_fin_year':
                    company_fiscalyear_dates = self.env.company.compute_fiscalyear_dates(last_fis_from)
                    date_from = company_fiscalyear_dates['date_from']
                    date_to = company_fiscalyear_dates['date_to']
                    dt_from = date_from - relativedelta(years=prev_period)
                    dt_to = date_to - relativedelta(years=prev_period)
                    domain = self._get_domain(account, dates, entry_type, journal_id, company_id)
                    domain += [('date', '>=', dt_from), ('date', '<=', dt_to)]
                    string = dt_to.strftime('%Y')
                    compare_period_names.append({'name': string})
                line_data = self.env['account.move.line'].read_group(domain, ['account_id', 'debit', 'credit'], ['account_id'])
                for ln in line_data:
                    inital_balance['debit'] += ln['debit']
                    inital_balance['credit'] += ln['credit']
                compare_period.append(inital_balance)
                prev_period -= 1
        return compare_period, compare_period_names

    def _get_report_vals(self, dates, entry_type, journal_id, company_id, prev_period, last_period):
        move_lines = []
        op_ic_lines = []
        op_ot_lines = []
        exp_lines = []
        dep_lines = []
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
        line_data = self.env['account.move.line'].read_group(domain, ['account_id', 'debit', 'credit'], ['account_id'])
        total_op_ic = 0.0
        total_op_ot = 0.0
        total_exp = 0.0
        total_dep = 0.0
        for ln in line_data:
            account = self.env['account.account'].browse(ln['account_id'][0])
            period_data, compare_period = self._get_period_data(account, dates, entry_type, journal_id, company_id, prev_period, last_period)
            vals = {
                'account': account.display_name,
                'debit': ln['debit'],
                'credit': ln['credit'],
                'period_data': period_data
            }
            if account.account_type == 'income':
                op_ic_lines.append(vals)
                total_op_ic += ln['debit'] - ln['credit']
            elif account.account_type == 'income_other':
                op_ot_lines.append(vals)
                total_op_ot += ln['debit'] - ln['credit']
            elif account.account_type in ['expense', 'expense_direct_cost']:
                exp_lines.append(vals)
                total_exp += ln['debit'] - ln['credit']
            elif account.account_type == 'expense_depreciation':
                dep_lines.append(vals)
                total_dep += ln['debit'] - ln['credit']
        currency_id = self.env.company.currency_id
        return {
            'move_lines': move_lines,
            'op_ic_lines': op_ic_lines,
            'op_ot_lines': op_ot_lines,
            'exp_lines': exp_lines,
            'dep_lines': dep_lines,
            'string': string,
            'currency_id': currency_id,
            'compare_period': compare_period,
            'total_op_ic': total_op_ic,
            'total_op_ot': total_op_ot,
            'total_exp': total_exp,
            'total_dep': total_dep,
            'net_profit': abs((total_op_ic + total_op_ot)) - abs((total_exp + total_dep))
        }

    @api.model
    def get_html(self, dates='this_month', entry_type='all', journal_id=False, company_id=False, prev_period=False, last_period=False):
        res = self._get_report_data()
        res['lines']['report_type'] = 'html'
        vals = self._get_report_vals(dates, entry_type, journal_id, company_id, prev_period, last_period)
        # res['lines'] = self.env.ref('account_financial_reports_knk.report_profit_loss_document')._render({'data': vals})
        res['lines'] = self.env['ir.ui.view']._render_template('account_financial_reports_knk.report_profit_loss_document', {'data': vals})
        res['selected_date_pl'] = vals['string']
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
        }

    def account_move_print_xls_report(self, **args):
        ctx = self.env.context
        vals = self._get_report_vals(dates=ctx.get('dates'), entry_type=ctx.get('entry_type'), journal_id=ctx.get('journal_id'), company_id=ctx.get('company_id'), prev_period=ctx.get('prev_period'), last_period=ctx.get('last_period'))
        return vals
