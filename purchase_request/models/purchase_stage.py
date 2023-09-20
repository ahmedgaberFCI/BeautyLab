
from odoo import models,fields,api,_


class PurchaseStage(models.Model):
    _name = "purchase.stage"
    _rec_name = 'name'
    _description = "Purchase Stage"

    name = fields.Char('Name', required=True)

