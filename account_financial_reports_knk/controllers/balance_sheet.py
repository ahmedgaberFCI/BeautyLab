# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.addons.account_financial_reports_knk.wizard import format_common


class BalanceSheetController(http.Controller):

    @http.route('/web/balance_sheet_report/export', type='http', auth='user')
    def export_xlsx(self, data, **kw):
        result = json.loads(data)
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour('gray_lighter', 0x21)
        workbook.set_colour_RGB(0x21, 224, 224, 224)
        M_header_tstyle = format_common.font_style(position='center', bold=1, fontos='black', font_height=220)
        small_text_left = format_common.font_style(position='left', fontos='black', border=1, font_height=180, color='grey')
        small_text_center = format_common.font_style(position='center', fontos='black', border=1, font_height=180, color='grey')
        small_text_right = format_common.font_style(position='right', fontos='black', border=1, font_height=180, color='grey')
        normal_text_right = format_common.font_style(position='right', fontos='black', border=1, font_height=180)
        sheet = workbook.add_sheet('Balance Sheet')
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(2, 2, col1, col1, ln.get('name'), small_text_center)
            col1 += 1
        sheet.write_merge(2, 2, col1, col1, result.get('string'), small_text_center)
        sheet.write_merge(0, 1, 0, 10, 'Balance Sheet', M_header_tstyle)
        sheet.write_merge(3, 3, 0, 2, _('ASSETS'), small_text_left)
        sheet.write_merge(4, 4, 0, 2, _('Current Assets'), small_text_center)
        sheet.write_merge(5, 5, 0, 2, _('Bank and Cash Accounts'), small_text_right)
        sheet.write_merge(6, 6, 0, 2, _('Receivables'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(3, 3, col1, col1, '')
            sheet.write_merge(4, 4, col1, col1, '')
            sheet.write_merge(5, 5, col1, col1, '')
            sheet.write_merge(6, 6, col1, col1, '')
            col1 += 1
        sheet.write_merge(3, 3, col1, col1, abs(result['total_bankcash']+result['total_receivable']+result['total_curr_assets']+result['total_prepayments']), small_text_right)
        sheet.write_merge(4, 4, col1, col1, abs(result['total_bankcash']+result['total_receivable']+result['total_curr_assets']+result['total_prepayments']), small_text_right)
        sheet.write_merge(5, 5, col1, col1, abs(result['total_bankcash']), small_text_right)
        sheet.write_merge(6, 6, col1, col1, abs(result['total_receivable']), small_text_right)
        row = 7
        for ln in result.get('rece_lines', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1

        sheet.write_merge(row, row, 0, 2, _('Current Assets'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_assets']), small_text_right)
        row += 1
        for ln in result.get('curr_assets', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1

        sheet.write_merge(row, row, 0, 2, _('Prepayments'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_prepayments']), small_text_right)
        row += 1
        for ln in result.get('prepayments', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1

        sheet.write_merge(row, row, 0, 2, _('Plus Fixed Assets'), small_text_center)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Plus Non-current Assets'), small_text_center)
        row += 2
        sheet.write_merge(row, row, 0, 2, _('LIABILITIES'), small_text_left)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_lia']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Current Liabilities'), small_text_center)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_lia']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Current Liabilities'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_lia']), small_text_right)
        row += 1
        for ln in result.get('curr_lia', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1
        sheet.write_merge(row, row, 0, 2, _('Payables'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_payables']), small_text_right)
        row += 1
        for ln in result.get('payables', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1
        sheet.write_merge(row, row, 0, 2, _('Non-Current Liabilities'), small_text_center)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_non_curr_lia']), small_text_right)
        row += 1
        for ln in result.get('non_curr_lia', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1

        row += 1
        sheet.write_merge(row, row, 0, 2, _('EQUITY'), small_text_left)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_alloc_earning']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Unallocated Earnings'), small_text_center)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_alloc_earning']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Current Year Unallocated Earnings'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_alloc_earning']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        row += 1
        for ln in result.get('curr_alloc_earning', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1
        for ln in result.get('curr_earning', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1
        sheet.write_merge(row, row, 0, 2, _('Previous Years Unallocated Earnings'), small_text_right)
        row += 1
        sheet.write_merge(row, row, 0, 2, _('Retained Earnings'), small_text_right)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_retained_earning']), small_text_right)
        row += 1
        for ln in result.get('retained_earning', []):
            col1 = 4
            sheet.write_merge(row, row, 0, 2, _(ln.get('account')), normal_text_right)
            for pd in ln['period_data']:
                sheet.write_merge(row, row, col1, col1, abs(pd['debit']-pd['credit']), normal_text_right)
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln['debit']-ln['credit']), normal_text_right)
            row += 1
        sheet.write_merge(row, row, 0, 2, _('LIABILITIES + EQUITY   '), small_text_left)
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(row, row, col1, col1, '')
            col1 += 1
        sheet.write_merge(row, row, col1, col1, abs(result['total_curr_lia']+result['total_payables']+result['total_non_curr_lia'])+abs(result['total_curr_alloc_earning']+result['total_payables']+result['total_non_curr_lia']), small_text_right)
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', 'attachment; filename=%s.xls' % 'Balance_Sheet')],
            # cookies={'fileToken': token}
        )
        workbook.save(response.stream)
        return response
