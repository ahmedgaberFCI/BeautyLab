# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportPartnerLedger(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_partnerledger'
    _description = 'Partner Ledger Report'

    # def _lines(self, data, partner):
    #     full_account = []
    #     currency = self.env['res.currency']
    #     query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
    #     reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
    #     params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
    #     query = """
    #         SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
    #         FROM """ + query_get_data[0] + """
    #         LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
    #         LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
    #         LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
    #         LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
    #         WHERE "account_move_line".partner_id = %s
    #             AND m.state IN %s
    #             AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
    #             ORDER BY "account_move_line".date"""
    #     self.env.cr.execute(query, tuple(params))
    #     res = self.env.cr.dictfetchall()
    #     sum = 0.0
    #     lang_code = self.env.context.get('lang') or 'en_US'
    #     lang = self.env['res.lang']
    #     lang_id = lang._lang_get(lang_code)
    #     date_format = lang_id.date_format
    #     for r in res:
    #         r['date'] = r['date']
    #         r['displayed_name'] = '-'.join(
    #             r[field_name] for field_name in ('move_name', 'ref', 'name')
    #             if r[field_name] not in (None, '', '/')
    #         )
    #         sum += r['debit'] - r['credit']
    #         r['progress'] = sum
    #         r['currency_id'] = currency.browse(r.get('currency_id'))
    #         full_account.append(r)
    #     return full_account
    #
    # def _sum_partner(self, data, partner, field):
    #     if field not in ['debit', 'credit', 'debit - credit']:
    #         return
    #     result = 0.0
    #     query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
    #     reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
    #
    #     params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
    #     query = """SELECT sum(""" + field + """)
    #             FROM """ + query_get_data[0] + """, account_move AS m
    #             WHERE "account_move_line".partner_id = %s
    #                 AND m.id = "account_move_line".move_id
    #                 AND m.state IN %s
    #                 AND account_id IN %s
    #                 AND """ + query_get_data[1] + reconcile_clause
    #     self.env.cr.execute(query, tuple(params))
    #
    #     contemp = self.env.cr.fetchone()
    #     if contemp is not None:
    #         result = contemp[0] or 0.0
    #     return result
    #
    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     if not data.get('form'):
    #         raise UserError(_("Form content is missing, this report cannot be printed."))
    #     data['computed'] = {}
    #
    #     obj_partner = self.env['res.partner']
    #     query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
    #     data['computed']['move_state'] = ['draft', 'posted']
    #     if data['form'].get('target_move', 'all') == 'posted':
    #         data['computed']['move_state'] = ['posted']
    #     result_selection = data['form'].get('result_selection', 'customer')
    #     if result_selection == 'supplier':
    #         data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
    #     elif result_selection == 'customer':
    #         data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
    #     else:
    #         data['computed']['ACCOUNT_TYPE'] = ['asset_receivable', 'liability_payable']
    #
    #     self.env.cr.execute("""
    #         SELECT a.id
    #         FROM account_account a
    #         WHERE a.account_type IN %s
    #         AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
    #     data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
    #     params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
    #     reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
    #     query = """
    #         SELECT DISTINCT "account_move_line".partner_id
    #         FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
    #         WHERE "account_move_line".partner_id IS NOT NULL
    #             AND "account_move_line".account_id = account.id
    #             AND am.id = "account_move_line".move_id
    #             AND am.state IN %s
    #             AND "account_move_line".account_id IN %s
    #             AND NOT account.deprecated
    #             AND """ + query_get_data[1] + reconcile_clause
    #     self.env.cr.execute(query, tuple(params))
    #     if data['form']['partner_ids']:
    #         partner_ids = data['form']['partner_ids']
    #     else:
    #         partner_ids = [res['partner_id'] for res in
    #                        self.env.cr.dictfetchall()]
    #     partners = obj_partner.browse(partner_ids)
    #     partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
    #
    #     return {
    #         'doc_ids': partner_ids,
    #         'doc_model': self.env['res.partner'],
    #         'data': data,
    #         'docs': partners,
    #         'time': time,
    #         'lines': self._lines,
    #         'sum_partner': self._sum_partner,
    #     }


    def _lines(self, data, partner):
        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        params = [partner.id, tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + \
                query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account

    def _sum_partner(self, data, partner, field):
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '

        params = [partner.id, tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        if contemp is not None:
            result = contemp[0] or 0.0
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(
            data['form'].get('used_context', {}))._query_get()
        data['computed']['move_state'] = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
                SELECT a.id
                FROM account_account a
                WHERE NOT a.deprecated""",
                            (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in
                                           self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']),
                  tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if data['form'][
            'reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        query = """
                SELECT DISTINCT "account_move_line".partner_id
                FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                WHERE "account_move_line".partner_id IS NOT NULL
                    AND "account_move_line".account_id = account.id
                    AND am.id = "account_move_line".move_id
                    AND am.state IN %s
                    AND "account_move_line".account_id IN %s
                    AND NOT account.deprecated
                    AND """ + query_get_data[1] + reconcile_clause

        self.env.cr.execute(query, tuple(params))
        # ---------------------Taking only selected partners---------------------------

        if data['form']['partner_ids']:
            partner_ids = data['form']['partner_ids']
        else:
            partner_ids = [res['partner_id'] for res in
                           self.env.cr.dictfetchall()]

        # -----------------------------------------------------------------------------
        # partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]

        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))

        # ---------------------To Add Initial Balance---------------------------
        if data['form']['initial_balance'] and data['form']['partner_ids']:
            print("LLLLLLL",data['form']['date_to'])


            partner_add_query = """select distinct a.partner_id,b.name from account_move_line a
                 join res_partner b on a.partner_id=b.id where partner_id is not null """

            if data['form']['date_from']:
                partner_query = f"and a.date > '{data['form']['date_from']}' order by name"
                partner_add_query += partner_query

            if not data['form']['date_from']:
                if data['form']['date_to']:
                    partner_query = f"and a.date < '{data['form']['date_to']}' order by name"
                    partner_add_query += partner_query

            self.env.cr.execute(partner_add_query)
            account_partner_ids = [a for (a, b) in
                                   self.env.cr.fetchall()]
            initial_partner_ids = []
            for rec in partner_ids:
                if rec in account_partner_ids:
                    initial_partner_ids.append(rec)
            new_query = ''
            add_query = f"""SELECT  c.name, sum(a.debit) as initial_debit, 
                sum(a.credit) as initial_credit
                from account_move_line a join account_move b 
                on a.move_id = b.id join res_partner c on a.partner_id = c.id 
                 where a.partner_id is not null 
                """

            if len(partner_ids) == 1:
                new_query = f" and a.partner_id = {partner_ids[0]}"
                add_query += new_query
            if len(partner_ids) > 1:
                new_query = f"and a.partner_id in {tuple(partner_ids)}"
                add_query += new_query
            if data['form']['date_from']:
                new_query = f"and a.date < '{data['form']['date_from']}'"
                add_query += new_query
            if not data['form']['date_from']:
                if data['form']['date_to']:
                    new_query = f"and a.date < '{data['form']['date_to']}'"
                    add_query += new_query
            if len(data['form']['journal_ids']) > 1:
                new_query = f"and b.journal_id in {tuple(data['form']['journal_ids'])}"
                add_query += new_query
            if len(data['form']['journal_ids']) == 1:
                new_query = f"and b.journal_id = {data['form']['journal_ids'][0]}"
                add_query += new_query

            if data['form'].get('target_move', 'all') == 'posted':
                new_query = "and b.state = 'posted'"
                add_query += new_query
            if data['form']['partner_ids']:
                new_query = "group by c.name order by c.name"
                add_query += new_query

            self.env.cr.execute(add_query)

            record = self.env.cr.dictfetchall()
            partners = obj_partner.browse(initial_partner_ids)
            partners = sorted(partners,
                              key=lambda x: (x.ref or '', x.name or ''))

            return {
                'doc_ids': partner_ids,
                'doc_model': self.env['res.partner'],
                'data': data,
                'docs': partners,
                'time': time,
                'lines': self._lines,
                'sum_partner': self._sum_partner,
                'response': record

            }
        # -----------------------------------------------------------------------------
        else:

            return {
                'doc_ids': partner_ids,
                'doc_model': self.env['res.partner'],
                'data': data,
                'docs': partners,
                'time': time,
                'lines': self._lines,
                'sum_partner': self._sum_partner,

            }
