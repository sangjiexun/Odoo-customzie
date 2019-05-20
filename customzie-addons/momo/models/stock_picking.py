# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    purchase_id = fields.Many2one(related="group_id.purchase_id", string="Purchase Order", store=True, readonly=False)
    product_line_picking_ids = fields.One2many('momo.product.line.picking', 'stock_picking_id', 'Product Line Picking',
                                               copy=True)

    @api.multi
    def action_stock_picking(self):
        self.ensure_one()
        view_id = self.env.ref('momo.view_stock_picking_form').id
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'view_id': view_id,
            'res_id': self.id,
            'context': context,
        }

    @api.multi
    def action_open_pl_group(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'momo.product.line.group',
            'res_id': self.group_id.product_line_group_id.id,
        }

    @api.multi
    def _create_product_line_picking(self):
        for picking in self:
            product_line_group = picking.group_id.product_line_group_id
            if product_line_group:
                for line in product_line_group.product_line_link_ids:
                    self.env['momo.product.line.picking'].create(
                        {'stock_picking_id': picking.id, 'product_line_id': line.product_line_id.id,
                         'barcode': line.barcode})
