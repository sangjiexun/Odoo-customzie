# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    marker_name = fields.Many2one(
        "marker.info", string="Marker Name")
    marker_product_no = fields.Char('Marker Product')
    product_no = fields.Char('Product No', readonly=True, index=True, copy=False, default='New')
    ceo_price = fields.Float(
        'Ceo Cost', company_dependent=True,
        groups="base_inherit.group_ceo",)
    spec_cpu = fields.Char('Spec Cpu')
    spec_memory = fields.Char('Spec Memory')
    spec_hard_disc = fields.Char('Spec HardDisk')
    spec_driver = fields.Char('Spec Driver')

    @api.model
    def create(self, vals):
        if vals.get('product_no', 'New') == 'New':
            vals['product_no'] = self.env['ir.sequence'].next_by_code('product.product')
        return super(ProductProduct, self).create(vals)


class MarkerInfo(models.Model):

    _name = 'marker.info'
    _description = 'Marker Info'
    _order = 'id'

    name = fields.Char('Marker', required=True, index=True)