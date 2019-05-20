# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    @api.multi
    def button_approve(self, force=False):
        result = super(PurchaseOrder, self).button_approve(force=force)
        self._create_product_line_creator()
        return result

    @api.multi
    def _create_product_line_creator(self):
        creator = self.env['momo.product.line.creator'].create(
            {'create_type': 'auto', 'purchase_id': self.id, 'init_location_id': '8', 'group_id': self.group_id.id})
        for order in self:
            for line in order.order_line:
                res = {
                    'product_line_creator_id': creator.id,
                    'product_id': line.product_id.id,
                    'need_qty': line.product_qty,
                }
                self.env['momo.product.line.creator.detail'].create(res)
        return True

    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id,
                'purchase_id': self.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }
