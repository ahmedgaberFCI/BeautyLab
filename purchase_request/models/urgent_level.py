
from odoo import models,fields,api,_


class UrgentLevel(models.Model):
    _name = "urgent.level"
    _rec_name = 'name'
    _description = "Urgent Level"

    name = fields.Char('Name', required=True)

