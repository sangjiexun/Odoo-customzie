# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    branch_code = fields.Char('Branch Code')
    branch_name = fields.Char('Branch Name')


