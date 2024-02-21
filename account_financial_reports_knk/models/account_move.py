# -*- coding: utf-8 -*-
import xlsxwriter

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def account_move_print_xls_report(self, args, **kwargs):
        workbook = xlsxwriter.Workbook('demo.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:A', 20)
        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Hello')
        workbook.close()
