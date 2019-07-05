# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.tools.float_utils import float_round

class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    attribute_display= fields.Char(compute='_compute_attribute_value', string='Attribute_display', store=True)

    @api.depends('attribute_value_ids', 'default_code')
    def _compute_attribute_value(self):
        for product in self:
            attribute_name = []
            attributes = self.env['product.attribute']
            for value in product.attribute_value_ids:
                attribute_name.append(value.name)
                #print(value)
            #print(attribute_name)
            product.attribute_display = '-'.join([str(i) for i in attribute_name])

