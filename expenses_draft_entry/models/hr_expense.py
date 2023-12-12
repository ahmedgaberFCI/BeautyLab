# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero

class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == 'draft':
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif expense.sheet_id.state == "approve" or expense.sheet_id.state == "post":
                expense.state = "approved"

            elif expense.sheet_id.state == "second_approve" or expense.sheet_id.state == "post":
                expense.state = "second_approve"
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
            else:
                expense.state = "done"

    state = fields.Selection(selection_add=[
        ('second_approve', "Second Approve"),('done',),
    ], ondelete={'second_approve': 'set default'})

    def _get_account_move_line_values_draft(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.sudo().employee_id.address_home_id.commercial_partner_id.id

            # source move line
            amount = taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                # 'tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])

            # taxes move lines
            for tax in taxes['taxes']:
                amount = tax['amount']
                amount_currency = False
                if different_currency:
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                    amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date) if different_currency else base_amount
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense



    def action_move_create_draft(self):
        move_group_by_sheet = self._get_account_move_by_sheet()

        move_line_values_by_expense = self._get_account_move_line_values()

        for expense in self:
            # get the account move of the related sheet
            move = move_group_by_sheet[expense.sheet_id.id]

            # get move line values
            move_line_values = move_line_values_by_expense.get(expense.id)

            # link move lines to move, and move to expense sheet
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            expense.sheet_id.write({'account_move_id': move.id})

            if expense.payment_mode == 'company_account':
                expense.sheet_id.paid_expense_sheets()

        # post the moves
        # for move in move_group_by_sheet.values():
        #     move._post()

        return move_group_by_sheet

    # def action_move_create_draft(self):
    #     '''
    #     main function that is called when trying to create the accounting entries related to an expense
    #     '''
    #     move_group_by_sheet = self._get_account_move_by_sheet()
    #
    #     move_line_values_by_expense = self._get_account_move_line_values_draft()
    #
    #     move_to_keep_draft = self.env['account.move']
    #
    #     company_payments = self.env['account.payment']
    #
    #     for expense in self:
    #         company_currency = expense.company_id.currency_id
    #         different_currency = expense.currency_id != company_currency
    #
    #         # get the account move of the related sheet
    #         move = move_group_by_sheet[expense.sheet_id.id]
    #
    #         # get move line values
    #         move_line_values = move_line_values_by_expense.get(expense.id)
    #         move_line_dst = move_line_values[-1]
    #         total_amount = move_line_dst['debit'] or -move_line_dst['credit']
    #         total_amount_currency = move_line_dst['amount_currency']
    #
    #         # create one more move line, a counterline for the total on payable account
    #         if expense.payment_mode == 'company_account':
    #             if not expense.sheet_id.bank_journal_id.default_credit_account_id:
    #                 raise UserError(_("No credit account found for the %s journal, please configure one.") % (
    #                     expense.sheet_id.bank_journal_id.name))
    #             journal = expense.sheet_id.bank_journal_id
    #             # create payment
    #             payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
    #             journal_currency = journal.currency_id or journal.company_id.currency_id
    #             payment = self.env['account.payment'].create({
    #                 'payment_method_id': payment_methods and payment_methods[0].id or False,
    #                 'payment_type': 'outbound' if total_amount < 0 else 'inbound',
    #                 'partner_id': expense.sudo().employee_id.address_home_id.commercial_partner_id.id,
    #                 'partner_type': 'supplier',
    #                 'journal_id': journal.id,
    #                 'payment_date': expense.date,
    #                 'state': 'draft',
    #                 'currency_id': expense.currency_id.id if different_currency else journal_currency.id,
    #                 'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
    #                 'name': expense.name,
    #             })
    #             move_line_dst['payment_id'] = payment.id
    #
    #         # link move lines to move, and move to expense sheet
    #         move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
    #         expense.sheet_id.write({'account_move_id': move.id})
    #
    #         if expense.payment_mode == 'company_account':
    #             company_payments |= payment
    #             if journal.post_at == 'bank_rec':
    #                 move_to_keep_draft |= move
    #
    #             expense.sheet_id.paid_expense_sheets()
    #
    #     company_payments.filtered(lambda x: x.journal_id.post_at == 'pay_val').write({'state': 'reconciled'})
    #     company_payments.filtered(lambda x: x.journal_id.post_at == 'bank_rec').write({'state': 'posted'})
    #
    #     # post the moves
    #     # for move in move_group_by_sheet.values():
    #     #     if move in move_to_keep_draft:
    #     #         continue
    #     #     move.post()
    #
    #     return move_group_by_sheet


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(selection_add=[
        ('second_approve', "Second Approve"),('post',)
    ],  ondelete={'second_approve': 'set default'})
    budget_controller = fields.Boolean(string="Budget Controller", tracking=True, copy=False)

    def action_second_approve(self):
        return self.write({'state': 'second_approve'})



    def action_sheet_move_create_draft(self):
        if any(sheet.state != 'second_approve' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved expense(s)."))

        if not self.budget_controller:
            raise ValidationError("Please , Wait Budget Controller Manager Approve")

        if any(not sheet.journal_id for sheet in self):
            raise UserError(_("Expenses must have an expense journal specified to generate accounting entries."))

        expense_line_ids = self.mapped('expense_line_ids')\
            .filtered(lambda r: not float_is_zero(r.total_amount, precision_rounding=(r.currency_id or self.env.company.currency_id).rounding))
        res = expense_line_ids.action_move_create_draft()

        if not self.accounting_date:
            self.accounting_date = self.account_move_id.date

        if self.payment_mode == 'own_account' and expense_line_ids:
            self.write({'state': 'post'})
        else:
            self.write({'state': 'done'})
        self.activity_update()
        return res






