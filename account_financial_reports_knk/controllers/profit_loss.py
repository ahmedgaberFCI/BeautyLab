# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.addons.account_financial_reports_knk.wizard import format_common


class ProfitLossController(http.Controller):

    @http.route('/web/profit_loss_report/export', type='http', auth='user')
    def export_xlsx(self, data, **kw):

        result = json.loads(data)
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour('gray_lighter', 0x21)
        workbook.set_colour_RGB(0x21, 224, 224, 224)
        M_header_tstyle = format_common.font_style(position='center', bold=1, fontos='black', font_height=220)
        small_text = format_common.font_style(position='center', fontos='black', border=1, font_height=180, color='grey')
        small_text_left = format_common.font_style(position='left', fontos='black', border=1, font_height=180, color='grey')
        small_text_center = format_common.font_style(position='center', fontos='black', border=1, font_height=180, color='grey')
        small_text_right = format_common.font_style(position='right', fontos='black', border=1, font_height=180, color='grey')
        normal_text_right = format_common.font_style(position='right', fontos='black', border=1, font_height=180)
        sheet = workbook.add_sheet('Profit and Loss')
        col1 = 4
        for ln in result.get('compare_period'):
            sheet.write_merge(2, 2, col1, col1, ln.get('name'), small_text)
            col1 += 1
        sheet.write_merge(2, 2, col1, col1, result.get('string'), small_text)
        sheet.write_merge(0, 1, 0, 10, _('Profit and Loss'), M_header_tstyle)
        sheet.write_merge(3, 3, 0, 2, _('Income'), small_text_left)
        # GROSS PROFIT
        sheet.write_merge(4, 4, 0, 2, _('Gross Profit'), small_text_center)
        col1 = 4
        for ln in result.get('compare_period'):
            col1 += 1
        sheet.write(4, col1, abs(result.get('total_op_ic')) + abs(result.get('total_op_ot')), small_text_right)
        # OPRATING INCOME
        sheet.write_merge(5, 5, 0, 2, 'Operating Income', small_text_right)
        sheet.write(5, col1, abs(result.get('total_op_ic')), small_text_right)
        row = 6
        for ln in result.get('op_ic_lines'):
            sheet.write_merge(row, row, 0, 2, ln.get('account'), normal_text_right)
            col1 = 4
            for j in ln.get('period_data'):
                sheet.write(row, col1, abs(j.get('debit') - j.get('debit')))
                col1 += 1
            sheet.write_merge(row, row, col1, col1, abs(ln.get('debit') - ln.get('credit')))
            row += 1
        # OTHER INCOME
        sheet.write_merge(8, 8, 0, 2, 'Other Income', small_text_center)
        col1 = 4
        for ln in result.get('compare_period'):
            col1 += 1
        sheet.write(8, col1, abs(result.get('total_op_ot')), small_text_right)
        sheet.write_merge(9, 9, 0, 2, 'Expenses', small_text_left)
        # Expenses
        sheet.write_merge(10, 10, 0, 2, 'Expenses', small_text_center)
        sheet.write(10, col1, abs(result.get('total_exp')), small_text_right)
        # Deprecation
        sheet.write_merge(11, 11, 0, 2, 'Depreciation', small_text_center)
        sheet.write(11, col1, abs(result.get('total_dep')), small_text_right)
        # NETPROFIT
        sheet.write_merge(13, 13, 0, 2, 'Net Profit', small_text_left)
        sheet.write(13, col1, abs(result.get('net_profit')), small_text_right)
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', 'attachment; filename=%s.xls' % 'Profit_Loss_Report')],
            # cookies={'fileToken': token}
        )
        workbook.save(response.stream)
        return response
