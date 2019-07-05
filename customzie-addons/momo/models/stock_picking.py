# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    purchase_id = fields.Many2one(related="group_id.purchase_id", string="Purchase Order", store=True, readonly=False)
    product_line_picking_ids = fields.One2many('momo.product.line.picking', 'stock_picking_id', 'Product Line Picking',
                                               copy=True)
    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group', index=True)
    scan_over = fields.Boolean('Scan Over', default=False)

    @api.multi
    def open_scan_pop(self):
        product_sacn = self.env['momo.product.scan'].search(
            ['&', ('picking_id', '=', self.id), ('picking_type_id', '=', self.picking_type_id.id)], limit=1)
        if product_sacn:
            res_id = product_sacn.id
        else:
            res_id = self.env['momo.product.scan'].create(
                {'picking_id': self.id, 'picking_name': self.name, 'picking_type_id': self.picking_type_id.id,
                 'product_line_group_id': self.product_line_group_id.id}).id
            if self.product_line_group_id and self.product_line_group_id.product_line_link_ids:
                for product_line_link in self.product_line_group_id.product_line_link_ids:
                    if product_line_link.linked:
                        self.env['momo.product.scan.line'].create(
                            {"product_line_id": product_line_link.product_line_id.id,
                             "location": product_line_link.product_line_id.current_location,
                             "barcode": product_line_link.product_line_id.barcode,
                             "product_name": product_line_link.product_line_id.product_name,
                             "product_id": product_line_link.product_id.id,
                             "product_scan_id": res_id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Product Scan',
            'res_model': 'momo.product.scan',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': res_id,
            'target': 'new',
        }

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
