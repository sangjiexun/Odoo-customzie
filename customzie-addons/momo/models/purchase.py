# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


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
        creator = self.env['momo.product.line.creator'].create({'remark': self.name, 'init_location_id': '8'})
        for order in self:
            for line in order.order_line:
                res = {
                    'product_line_creator_id': creator.id,
                    'product_id': line.product_id.id,
                    'need_qty': line.product_qty,
                }
                self.env['momo.product.line.creator.detail'].create(res)
        return True
