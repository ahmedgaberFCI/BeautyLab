# Copyright 2018-2019 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


_STATES = [
    ("draft", "Draft"),
    ("to_approve", "To be approved"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
    ("done", "Done"),
]


class PurchaseRequest(models.Model):

    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    @api.model
    def _company_get(self):
        return self.env["res.company"].browse(self.env.company.id)

    @api.model
    def _get_default_requested_by(self):
        return self.env["res.users"].browse(self.env.uid)

    @api.model
    def _get_default_name(self):
        return self.env["ir.sequence"].next_by_code("purchase.request")

    @api.model
    def _default_picking_type(self):
        type_obj = self.env["stock.picking.type"]
        company_id = self.env.context.get("company_id") or self.env.company.id
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.company_id", "=", company_id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id", "=", False)]
            )
        return types[:1]

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("to_approve", "approved", "rejected", "done"):
                rec.is_editable = False
            else:
                rec.is_editable = True

    name = fields.Char(
        string="Request Reference",
        required=True,
        default=_get_default_name,

    )
    origin = fields.Char(string="Source Document")
    recommend_vendor = fields.Char(string="Recommended Vendor")
    date_start = fields.Date(
        string="Creation date",
        help="Date when the user initiated the " "request.",
        default=fields.Date.context_today,

    )

    approve_date = fields.Date(string="Approve date",copy=False)

    end_date = fields.Date(string="End date",help="Date when the user initiated the " "request.",)

    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested by",
        required=True,
        copy=False,

        default=_get_default_requested_by,
    )
    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("purchase_request.group_purchase_request_manager").id,
            )
        ],
    )
    description = fields.Text(string="Description")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_company_get,

    )
    line_ids = fields.One2many(
        comodel_name="purchase.request.line",
        inverse_name="request_id",
        string="Products to Purchase",
        readonly=False,
        copy=True,
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        related="line_ids.product_id",
        string="Product",
        readonly=True,
    )
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        required=True,
        copy=False,
        default="draft",
    )
    is_editable = fields.Boolean(
        string="Is editable", compute="_compute_is_editable", readonly=True
    )
    to_approve_allowed = fields.Boolean(compute="_compute_to_approve_allowed")
    picking_type_id = fields.Many2one(
        comodel_name="stock.picking.type",
        string="Picking Type",
        default=_default_picking_type,
    )
    group_id = fields.Many2one(
        comodel_name="procurement.group", string="Procurement Group", copy=False
    )
    urgent_level_id = fields.Many2one(comodel_name="urgent.level", string="Urgent Level",)

    purchase_stages_id = fields.Many2one(comodel_name="purchase.stage", string="PR Stage",)
    purchase_types_id = fields.Many2one(comodel_name="purchase.types", string="PR Type",)
    type_checked = fields.Boolean(string="Checked",related="purchase_types_id.checked")

    sale_market_approve = fields.Boolean("Sales & Marketing Approve")

    type_assigned_to_id = fields.Many2one(
        comodel_name="res.users",
        string="Owner Approve",
        domain=lambda self: [
            (
                "groups_id",
                "in",
                self.env.ref("base.group_system").id,
            )
        ],
    )

    notes = fields.Text(string="Notes")

    line_count = fields.Integer(
        string="Purchase Request Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    move_count = fields.Integer(
        string="Stock Move count", compute="_compute_move_count", readonly=True
    )
    purchase_count = fields.Integer(
        string="Purchases count", compute="_compute_purchase_count", readonly=True
    )

    def calc_total_estimated_cost(self):
        x = 0.0
        for rec in self.line_ids:
            print("4444444444",rec.estimated_cost)
            x += rec.estimated_cost

        self.total_estimated_cost = x


    total_estimated_cost = fields.Float(string="Estimated Cost",compute="calc_total_estimated_cost")

    owner_confirm = fields.Boolean(string="Owner Confirm",)

    owner_confirm = fields.Selection(
        [
            ("confirm", "confirm"),

        ],
        string="Owner Confirm",

    )
    budget_controller = fields.Boolean(string="Budget Controller", tracking=True, copy=False)

    @api.depends('budget_controller')
    def calc_budget_controller_date(self):
        for rec in self:
            if rec.budget_controller == True:
                rec.budget_controller_date = fields.Date.today()
                PR_Users = self.env.ref('purchase_request.group_pr_schedule_activity_todo').users
                print("$$$$$$$",PR_Users)
                if PR_Users:
                    for user in PR_Users:
                        won_vals = {
                            'activity_type_id': 4,
                            # 'activity_type_id': self.stage_id.activity_type_id.default_next_type_id.id,
                            'summary': rec.name + " " + "has been approved by budget controller",
                            'automated': True,
                            'note': rec.name,
                            'date_deadline': fields.Date.context_today(self),
                            'res_model_id': 908,
                            'res_id': rec._origin.id,
                            'user_id': user.id
                        }
                        print(won_vals)
                        scheduled_activity_PR = self.env['mail.activity'].sudo().create(won_vals)
                        print("@@@@@@@@", scheduled_activity_PR)
            else:
                rec.budget_controller_date = False

    budget_controller_date = fields.Date(string="Budget Controll Date",compute="calc_budget_controller_date",store=True)


    @api.depends('type_assigned_to_id')
    def calc_type_assigned_to_id(self):
        if self.type_assigned_to_id and self.type_checked or self.total_estimated_cost >= 25000:
            self.to_check = True
        else:
            self.to_check = False

    to_check = fields.Boolean(string="To check ",compute="calc_type_assigned_to_id")


    @api.depends("line_ids")
    def _compute_purchase_count(self):
        self.purchase_count = len(self.mapped("line_ids.purchase_lines.order_id"))

    def action_view_purchase_order(self):
        action = self.env.ref("purchase.purchase_rfq").sudo().read()[0]
        lines = self.sudo().mapped("line_ids.purchase_lines.order_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_move_count(self):
        self.move_count = len(
            self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        )

    def action_view_stock_move(self):
        action = self.env.ref("stock.stock_move_action").read()[0]
        # remove default filters
        action["context"] = {}
        lines = self.mapped("line_ids.purchase_request_allocation_ids.stock_move_id")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [(self.env.ref("stock.view_move_form").id, "form")]
            action["res_id"] = lines.id
        return action

    @api.depends("line_ids")
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.mapped("line_ids"))

    def action_view_purchase_request_line(self):
        action = self.env.ref(
            "purchase_request.purchase_request_line_form_action"
        ).read()[0]
        lines = self.mapped("line_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", lines.ids)]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase_request.purchase_request_line_form").id, "form")
            ]
            action["res_id"] = lines.ids[0]
        return action

    @api.depends("state", "line_ids.product_qty", "line_ids.cancelled")
    def _compute_to_approve_allowed(self):
        for rec in self:
            rec.to_approve_allowed = rec.state == "draft" and any(
                [not line.cancelled and line.product_qty for line in rec.line_ids]
            )

    def copy(self, default=None):
        default = dict(default or {})
        self.ensure_one()
        default.update(
            {
                "state": "draft",
                "name": self.env["ir.sequence"].next_by_code("purchase.request"),
            }
        )
        return super(PurchaseRequest, self).copy(default)

    @api.model
    def _get_partner_id(self, request):
        user_id = request.assigned_to or self.env.user
        return user_id.partner_id.id

    @api.model
    def create(self, vals):
        request = super(PurchaseRequest, self).create(vals)
        if vals.get("assigned_to"):
            partner_id = self._get_partner_id(request)
            request.message_subscribe(partner_ids=[partner_id])
        return request

    def write(self, vals):
        res = super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get("assigned_to"):
                partner_id = self._get_partner_id(request)
                request.message_subscribe(partner_ids=[partner_id])
        return res

    def _can_be_deleted(self):
        self.ensure_one()
        return self.state == "draft"

    def unlink(self):
        for request in self:
            if not request._can_be_deleted():
                raise UserError(
                    _("You cannot delete a purchase request which is not draft.")
                )
        return super(PurchaseRequest, self).unlink()

    def button_draft(self):
        self.mapped("line_ids").do_uncancel()
        return self.write({"state": "draft"})

    def button_to_approve(self):

        self.to_approve_allowed_check()
        return self.write({"state": "to_approve"})

    def button_approved(self):
        # if self.department_id.for_approve and not self.sale_market_approve:
        #     raise ValidationError("Please , Wait Sales & Marketing Department Approve")

        return self.write({"state": "approved",'approve_date':fields.Date.today()})

    def button_rejected(self):
        self.mapped("line_ids").do_cancel()
        return self.write({"state": "rejected"})

    def button_done(self):
        return self.write({"state": "done"})

    def check_auto_reject(self):
        """When all lines are cancelled the purchase request should be
        auto-rejected."""
        for pr in self:
            if not pr.line_ids.filtered(lambda l: l.cancelled is False):
                pr.write({"state": "rejected"})

    def to_approve_allowed_check(self):
        for rec in self:
            if not rec.to_approve_allowed:
                raise UserError(
                    _(
                        "You can't request an approval for a purchase request "
                        "which is empty. (%s)"
                    )
                    % rec.name
                )
