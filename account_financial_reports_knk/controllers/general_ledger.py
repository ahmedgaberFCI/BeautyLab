# -*- coding: utf-8 -*-
import json
from odoo import http, _
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.addons.account_financial_reports_knk.wizard import format_common


class GeneralLedgerController(http.Controller):

    @http.route('/web/general_ledger_report/export', type='http', auth='user')
    def export_xlsx(self, data, **kw):
        result = json.loads(data)
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour('gray_lighter', 0x21)
        workbook.set_colour_RGB(0x21, 224, 224, 224)
        M_header_tstyle = format_common.font_style(position='center', bold=1, fontos='black', font_height=220)
        small_text_left = format_common.font_style(position='left', fontos='black', border=1, font_height=180)
        small_text_center = format_common.font_style(position='center', fontos='black', border=1, font_height=180)
        bold_text_center = format_common.font_style(position='center', fontos='black', border=1, font_height=180, color="grey")
        sheet = workbook.add_sheet('General Ledger')
        sheet.write_merge(0, 1, 0, 10, _('General Ledger'), M_header_tstyle)
        sheet.write_merge(2, 2, 0, 2, '')
        sheet.write(2, 3, _('Date'), bold_text_center)
        sheet.write(2, 4, _('Communication'), bold_text_center)
        sheet.write(2, 5, _('Partner'), bold_text_center)
        sheet.write(2, 6, _('Currency'), bold_text_center)
        sheet.write(2, 7, _('Debit'), bold_text_center)
        sheet.write(2, 8, _('Credit'), bold_text_center)
        sheet.write(2, 9, _('Balance'), bold_text_center)
        row = 3
        for ln in result.get('move_lines'):
            sheet.write_merge(row, row, 0, 2, ln['account'], small_text_left)
            sheet.write(row, 3, ln['date'], small_text_center)
            sheet.write(row, 4, ln['name'], small_text_center)
            sheet.write(row, 5, ln['partner'], small_text_center)
            sheet.write(row, 6, ln['amount_currency'], small_text_center)
            sheet.write(row, 7, ln['debit'], small_text_center)
            sheet.write(row, 8, ln['credit'], small_text_center)
            sheet.write(row, 9, ln['debit']-ln['credit'], small_text_center)
            row += 1
        response = request.make_response(
            None,
            headers=[('Content-Type', 'application/vnd.ms-excel'), ('Content-Disposition', 'attachment; filename=%s.xls' % 'General_Ledger')],
            # cookies={'fileToken': token}
        )
        workbook.save(response.stream)
        return response
