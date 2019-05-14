# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
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
