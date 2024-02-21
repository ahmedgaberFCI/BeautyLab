# -*- coding: utf-8 -*-
from odoo import fields, models


class output(models.Model):
    _name = 'output'
    _description = "Excel Output"

    name = fields.Char('Name', size=256)
    xls_output = fields.Binary('Excel output', readonly=True)
