# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.addons.account_financial_reports_knk.wizard import format_common


class TrialBalanceController(http.Controller):

    @http.route('/web/trial_balance_report/export', type='http', auth='user')
    def export_xlsx(self, data, **kw):

        result = json.loads(data)
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour('gray_lighter', 0x21)
        workbook.set_colour_RGB(0x21, 224, 224, 224)
        M_header_tstyle = format_common.font_style(position='center', bold=1, fontos='black', font_height=220)
        small_text = format_common.font_style(position='center', bold=1, fontos='black', border=1, font_height=180, color='grey')

        sheet = workbook.add_sheet('Trial Balance')

        sheet.write_merge(0, 1, 0, 10, 'Trial Balance', M_header_tstyle)
        sheet.write_merge(2, 2, 0, 2, '')
        sheet.write_merge(2, 2, 3, 4, 'Initial Balance', small_text)
        sheet.write_merge(3, 3, 3, 3, 'Debits',  small_text)
        sheet.write_merge(3, 3, 4, 4, 'Credits',  small_text)
        col1 = 5
        col2 = 6
        tot_init_credit = 0
        tot_init_debit = 0
        tot_credit = 0
        tot_debit = 0

        for ln in result.get('compare_period'):
            sheet.write_merge(2, 2, col1, col2, ln.get('name'), small_text)
            sheet.write_merge(3, 3, col1, col1, 'Debits',  small_text)
            sheet.write_merge(3, 3, col2, col2, 'Credits',  small_text)
            col1 += 2
            col2 += 2
        sheet.write_merge(2, 2, col1, col2, result.get('string'), small_text)
        sheet.write_merge(3, 3, col1, col1, 'Debits',  small_text)
        sheet.write_merge(3, 3, col2, col2, 'Credits',  small_text)
        row = 5
        for ln in result.get('move_lines'):
            col1 = 5
            col2 = 6
            sheet.write_merge(row, row, 0, 2, ln.get('account'))
            sheet.write(row, 3, ln.get('init_debit'))
            sheet.write(row, 4, ln.get('init_credit'))
            for j in ln.get('period_data'):
                sheet.write(row, col1, j.get('debit'))
                sheet.write(row, col2, j.get('credit'))
                col1 += 2
                col2 += 2
            sheet.write(row, col1, ln.get('debit'))
            sheet.write(row, col2, ln.get('credit'))
            tot_init_credit += ln.get('init_credit')
            tot_init_debit += ln.get('init_debit')
            tot_credit += ln.get('credit')
            tot_debit += ln.get('debit')
            row += 1
        col1 += 2
        col2 += 2
        sheet.write_merge(2, 2, col1, col2, 'Total', small_text)
        sheet.write_merge(3, 3, col1, col1, 'Debits',  small_text)
        sheet.write_merge(3, 3, col2, col2, 'Credits',  small_text)
        row = 5
        for ln in result.get('move_lines'):
            sheet.write(row, col1, ln.get('init_debit') + ln.get('debit'))
            sheet.write(row, col2, ln.get('init_credit') + ln.get('credit'))
            row += 1
        sheet.write(row, 0, 'Total', small_text)
        sheet.write(row, 3, tot_init_debit, small_text)
        sheet.write(row, 4, tot_init_credit, small_text)

        col1 = 5
        col2 = 6
        for ln in result.get('compare_period'):
            col1 += 2
            col2 += 2
        sheet.write(row, col1, tot_debit, small_text)
        sheet.write(row, col2, tot_credit, small_text)
        col1 += 2
        col2 += 2
        sheet.write(row, col1, tot_init_debit+tot_debit, small_text)
        sheet.write(row, col2, tot_init_credit+tot_credit, small_text)
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', 'attachment; filename=%s.xls' % 'Trial_Balance_Report')],
            # cookies={'fileToken': token}
        )
        workbook.save(response.stream)
        return response
