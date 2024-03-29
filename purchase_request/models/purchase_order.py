# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, exceptions, fields, models

from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_types_id = fields.Many2one(comodel_name="purchase.types", string="PO Types", required=True ,ondelete='restrict')

    cfo_confirm = fields.Boolean(string="Supply Chain Approver", tracking=True, copy=False)

    chairman_confirm = fields.Boolean(string="Chairman Confirm", tracking=True, copy=False)

    budget_controller = fields.Boolean(string="Budget Controller", tracking=True, copy=False)

    purchase_manager_approver = fields.Boolean(string="Purchaing Manager Approver", tracking=True, copy=False)

    # =========
    # new fields
    # ===========
    cfo_confirm_date = fields.Datetime(string="Supply Chain Approver Date", tracking=True, copy=False)

    chairman_confirm_date = fields.Datetime(string="Chairman Confirm Date", tracking=True, copy=False)

    budget_controller_date = fields.Datetime(string="Budget Controller Date", tracking=True, copy=False)

    purchase_manager_approver_date = fields.Datetime(string="Purchaing Manager Approver Date", tracking=True,
                                                     copy=False)

    confirm_action_date = fields.Datetime(string="Confirm Action Date", tracking=True, copy=False)

    approve_action_date = fields.Datetime(string="Approve Action Date", tracking=True, copy=False)

    @api.onchange('cfo_confirm')
    def onchange_cfo_confirm(self):
        if self.cfo_confirm:
            self.cfo_confirm_date = fields.Datetime.now()
        else:
            self.cfo_confirm_date = False

    @api.onchange('chairman_confirm')
    def onchange_chairman_confirm(self):
        if self.chairman_confirm:
            self.chairman_confirm_date = fields.Datetime.now()
        else:
            self.chairman_confirm_date = False

    @api.onchange('budget_controller')
    def onchange_budget_controller(self):
        if self.budget_controller:
            self.budget_controller_date = fields.Datetime.now()
        else:
            self.budget_controller_date = False

    @api.onchange('purchase_manager_approver')
    def onchange_purchase_manager_approver(self):
        if self.purchase_manager_approver:
            self.purchase_manager_approver_date = fields.Datetime.now()
        else:
            self.purchase_manager_approver_date = False

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for rec in self:
            rec.write({'cfo_confirm': False, 'chairman_confirm': False, 'budget_controller': False,
                       'purchase_manager_approver': False,
                       'cfo_confirm_date': False, 'chairman_confirm_date': False, 'budget_controller_date': False,
                       'purchase_manager_approver_date': False,
                       })
        return res

    def _track_subtype(self, init_values):
        # OVERRIDE to log a different message when an invoice is paid using SDD.
        self.ensure_one()
        if 'cfo_confirm' in init_values:
            return self.env.ref('purchase_request.tracking_cfo_chairman')

        if 'chairman_confirm' in init_values:
            return self.env.ref('purchase_request.tracking_cfo_chairman_confirm')

        if 'budget_controller' in init_values:
            return self.env.ref('purchase_request.tracking_budget_controller_confirm')
        if 'purchase_manager_approver' in init_values:
            return self.env.ref('purchase_request.tracking_purchase_manager_approver_confirm')
        return super(PurchaseOrder, self)._track_subtype(init_values)

    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve()
        if not self.purchase_manager_approver:
            raise ValidationError("Please , Wait Purchasing Manager Approve")

        if self.purchase_types_id.budget_controller:
            print("$$$$$$$$$$$$$$")

            # if self.env.user.has_group('base.group_system'):
            if not self.budget_controller:
                raise ValidationError("Please , Wait Budget Controller Manager Approve")

        if self.purchase_types_id.checked:
            print("$$$$$$$$$$$$$$")

            # if self.env.user.has_group('base.group_system'):
            if not self.chairman_confirm:
                raise ValidationError("Please , Wait Chairman Approver")
            else:
                self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
                self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
                return {}

        else:
            if self.currency_id.id == 76:

                # if self.amount_total > 250000 and self.amount_total < 500000:
                if self.amount_total >= 1 and self.amount_total < 500000:
                    if not self.cfo_confirm:
                        raise ValidationError("Please, Wait Supply Chain Manager Approve")
                if self.amount_total >= 500000:
                    if not self.cfo_confirm:
                        raise ValidationError("Please, Wait Supply Chain Manager Approve")
                    if not self.chairman_confirm:
                        raise ValidationError("Please, Wait Chairman Approve")
            if self.currency_id.id in [1, 2]:
                # if self.amount_total > 9000 and self.amount_total < 14000:
                if self.amount_total >= 1 and self.amount_total < 14000:
                    if not self.cfo_confirm:
                        raise ValidationError("Please, Wait Supply Chain Manager Approve")
                if self.amount_total >= 14000:
                    if not self.cfo_confirm:
                        raise ValidationError("Please, Wait Supply Chain Manager Approve")
                    if not self.chairman_confirm:
                        raise ValidationError("Please, Wait Chairman Approve")

        self.write({
            'approve_action_date':fields.Datetime.now()
        })

        return res
        # else:
        #     print("^^^^^^^^^^^^^6")
        #     self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
        #     self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
        #     return {}

    def send_notificaion(self):

        # create condition only receipt document
        if self.chairman_confirm:

            notification_ids = []
            body = "Purchase Order # " + str(self.name) + "  has approved by chairman"
            for purchase in self.user_id:
                notification_ids.append((0, 0, {
                    'res_partner_id': purchase.partner_id.id,
                    'notification_type': 'inbox'}))
            self.sudo().message_post(body=body, message_type='notification',
                                     subtype_xmlid='mail.mt_comment', author_id=self.user_id.partner_id.id,
                                     notification_ids=notification_ids, partner_ids=[self.user_id.partner_id.id], )

    # def send_notificaion(self):
    #     body = "Purchase Order # " + str(self.name) + "  has approved by chairman"
    #     print("$$$$$$$$$$$$$$$$$4",{'message_type': "email",
    #                                     'subtype': 'mail.mt_comment',  # subject type
    #                                      'body': body,
    #                                      'subject': "Message subject",
    #                                      'partner_ids': [(4, self.user_id.partner_id.id)],
    #                                      # partner to whom you send notification
    #                                      'model': self._name,
    #                                      'res_id': self.id,
    #                                      })
    #     x= self.env['mail.message'].create({'message_type': "notification",
    #                                      'body': body,
    #                                      'subject': "Message subject",
    #                                      'partner_ids': [self.user_id.partner_id.id],
    #                                      # partner to whom you send notification
    #                                      'model': self._name,
    #                                      'res_id': self.id,
    #                                      })
    #     print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",x)

    # def button_approve(self, force=False):
    #     if self.purchase_types_id and self.purchase_types_id.checked:
    #         if self.env.user.has_group('base.group_system'):
    #             self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
    #             self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
    #             return {}
    #         else:
    #             raise ValidationError("Please , Wait Chairman Approver")
    #     else:
    #         print("^^^^^^^^^^^^^6")
    #         self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
    #         self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done'})
    #         return {}

    def _purchase_request_confirm_message_content(self, request, request_dict=None):
        self.ensure_one()
        if not request_dict:
            request_dict = {}
        title = _("Order confirmation %s for your Request %s") % (
            self.name,
            request.name,
        )
        message = "<h3>%s</h3><ul>" % title
        message += _(
            "The following requested items from Purchase Request %s "
            "have now been confirmed in Purchase Order %s:"
        ) % (request.name, self.name)

        for line in request_dict.values():
            message += _(
                "<li><b>%s</b>: Ordered quantity %s %s, Planned date %s</li>"
            ) % (
                           line["name"],
                           line["product_qty"],
                           line["product_uom"],
                           line["date_planned"],
                       )
        message += "</ul>"
        return message

    def _purchase_request_confirm_message(self):
        request_obj = self.env["purchase.request"]
        for po in self:
            requests_dict = {}
            for line in po.order_line:
                for request_line in line.sudo().purchase_request_lines:
                    request_id = request_line.request_id.id
                    if request_id not in requests_dict:
                        requests_dict[request_id] = {}
                    date_planned = "%s" % line.date_planned
                    data = {
                        "name": request_line.name,
                        "product_qty": line.product_qty,
                        "product_uom": line.product_uom.name,
                        "date_planned": date_planned,
                    }
                    requests_dict[request_id][request_line.id] = data
            for request_id in requests_dict:
                request = request_obj.sudo().browse(request_id)
                message = po._purchase_request_confirm_message_content(
                    request, requests_dict[request_id]
                )
                request.message_post(body=message, subtype_xmlid="mail.mt_comment")
        return True

    def _purchase_request_line_check(self):
        for po in self:
            for line in po.order_line:
                for request_line in line.purchase_request_lines:
                    if request_line.sudo().purchase_state == "done":
                        raise exceptions.UserError(
                            _("Purchase Request %s has already " "been completed")
                            % request_line.request_id.name
                        )
        return True

    def button_confirm(self):
        if self.amount_total <= 50000 and self.env.user.has_group(
                'purchase_request.group_pr_specialist_user') and not self.purchase_types_id.budget_controller and not self.purchase_types_id.checked:
            # self = self.filtered(lambda order: order._approval_allowed())
            # pick=
            # print("KKKK========",pick)
            self.write({'state': 'purchase', 'date_approve': fields.Datetime.now()})
            self.filtered(lambda p: p.company_id.po_lock == 'lock').write({'state': 'done',})
        # self._purchase_request_line_check()


        res = super(PurchaseOrder, self).button_confirm()
        self._create_picking()
        self.write({
            'confirm_action_date': fields.Datetime.now()
        })

        self._purchase_request_confirm_message()

        return res

    def unlink(self):
        alloc_to_unlink = self.env["purchase.request.allocation"]
        for rec in self:
            for alloc in (
                    rec.order_line.mapped("purchase_request_lines")
                            .mapped("purchase_request_allocation_ids")
                            .filtered(lambda alloc: alloc.purchase_line_id.order_id.id == rec.id)
            ):
                alloc_to_unlink += alloc
        res = super().unlink()
        alloc_to_unlink.unlink()
        return res

    def write(self, vals):
        #  As services do not generate stock move this tweak is required
        #  to allocate them.
        res = super(PurchaseOrder, self).write(vals)
        print("res ===", res)

        if vals.get("chairman_confirm"):

            notification_ids = []
            body = "Purchase Order # " + str(self.name) + "  has been approved by chairman"
            for purchase in self.user_id:
                notification_ids.append((0, 0, {
                    'res_partner_id': purchase.partner_id.id,
                    'notification_type': 'inbox'}))
            self.sudo().message_post(body=body, message_type='notification', subtype_xmlid='mail.mt_comment',
                                     author_id=self.user_id.partner_id.id,
                                     notification_ids=notification_ids, partner_ids=[self.user_id.partner_id.id], )
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_lines = fields.Many2many(
        comodel_name="purchase.request.line",
        relation="purchase_request_purchase_order_line_rel",
        column1="purchase_order_line_id",
        column2="purchase_request_line_id",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    purchase_request_allocation_ids = fields.One2many(
        comodel_name="purchase.request.allocation",
        inverse_name="purchase_line_id",
        string="Purchase Request Allocation",
        copy=False,
    )

    def action_openRequestLineTreeView(self):
        """
        :return dict: dictionary value for created view
        """
        request_line_ids = []
        for line in self:
            request_line_ids += line.purchase_request_lines.ids

        domain = [("id", "in", request_line_ids)]

        return {
            "name": _("Purchase Request Lines"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.request.line",
            "view_mode": "tree,form",
            "domain": domain,
        }

    def _prepare_stock_moves(self, picking):
        self.ensure_one()
        val = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        all_list = []
        for v in val:
            all_ids = self.env["purchase.request.allocation"].search(
                [("purchase_line_id", "=", v["purchase_line_id"])]
            )
            for all_id in all_ids:
                all_list.append((4, all_id.id))
            v["purchase_request_allocation_ids"] = all_list
        return val

    def update_service_allocations(self, prev_qty_received):
        for rec in self:
            allocation = self.env["purchase.request.allocation"].search(
                [
                    ("purchase_line_id", "=", rec.id),
                    ("purchase_line_id.product_id.type", "=", "service"),
                ]
            )
            if not allocation:
                return
            qty_left = rec.qty_received - prev_qty_received
            for alloc in allocation:
                allocated_product_qty = alloc.allocated_product_qty
                if not qty_left:
                    alloc.purchase_request_line_id._compute_qty()
                    break
                if alloc.open_product_qty <= qty_left:
                    allocated_product_qty += alloc.open_product_qty
                    qty_left -= alloc.open_product_qty
                    alloc._notify_allocation(alloc.open_product_qty)
                else:
                    allocated_product_qty += qty_left
                    alloc._notify_allocation(qty_left)
                    qty_left = 0
                alloc.write({"allocated_product_qty": allocated_product_qty})

                message_data = self._prepare_request_message_data(
                    alloc, alloc.purchase_request_line_id, allocated_product_qty
                )
                message = self._purchase_request_confirm_done_message_content(
                    message_data
                )
                alloc.purchase_request_line_id.request_id.message_post(
                    body=message, subtype_xmlid="mail.mt_comment"
                )

                alloc.purchase_request_line_id._compute_qty()
        return True

    @api.model
    def _purchase_request_confirm_done_message_content(self, message_data):
        title = _("Service confirmation for Request %s") % (
            message_data["request_name"]
        )
        message = "<h3>%s</h3>" % title
        message += _(
            "The following requested services from Purchase"
            " Request %s requested by %s "
            "have now been received:"
        ) % (message_data["request_name"], message_data["requestor"])
        message += "<ul>"
        message += _("<li><b>%s</b>: Received quantity %s %s</li>") % (
            message_data["product_name"],
            message_data["product_qty"],
            message_data["product_uom"],
        )
        message += "</ul>"
        return message

    def _prepare_request_message_data(self, alloc, request_line, allocated_qty):
        return {
            "request_name": request_line.request_id.name,
            "product_name": request_line.product_id.name_get()[0][1],
            "product_qty": allocated_qty,
            "product_uom": alloc.product_uom_id.name,
            "requestor": request_line.request_id.requested_by.partner_id.name,
        }

    def write(self, vals):
        #  As services do not generate stock move this tweak is required
        #  to allocate them.

        if vals.get("chairman_confirm"):
            print("RRRRRRRRRRRRRRRRRRRRr")

            notification_ids = []
            body = "Purchase Order # " + str(vals.get("name")) + "  has approved by chairman"
            for purchase in vals.get("user_id"):
                notification_ids.append((0, 0, {
                    'res_partner_id': purchase.partner_id.id,
                    'notification_type': 'inbox'}))
            self.sudo().message_post(body=body, message_type='notification',
                                     subtype_xmlid='mail.mt_comment', author_id=vals.get("user_id").partner_id.id,
                                     notification_ids=notification_ids,
                                     partner_ids=[vals.get("user_id").partner_id.id], )
        prev_qty_received = {}
        if vals.get("qty_received", False):
            service_lines = self.filtered(lambda l: l.product_id.type == "service")
            for line in service_lines:
                prev_qty_received[line.id] = line.qty_received
        res = super(PurchaseOrderLine, self).write(vals)
        if prev_qty_received:
            for line in service_lines:
                line.update_service_allocations(prev_qty_received[line.id])

        return res
