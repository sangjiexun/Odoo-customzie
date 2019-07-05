# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    assemble_id = fields.Many2one('nashi.assemble', 'Assemble Order')
    lot_produced_id = fields.Many2one('stock.production.lot', 'Finished Lot/Serial Number')
    lot_produced_qty = fields.Float(
        'Quantity Finished Product', digits=dp.get_precision('Product Unit of Measure'),
        help="Informative, not used in matching")
    done_move = fields.Boolean('Move Done', related='move_id.is_done', readonly=False, store=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    assemble_id = fields.Many2one(
        'nashi.assemble', 'Assemble Order for finished products')
    pick_assemble_id = fields.Many2one(
        'nashi.assemble', 'Assemble Order for pick products')

    # Quantities to process, in normalized UoMs

    is_done = fields.Boolean(
        'Done', compute='_compute_is_done',
        store=True,
        help='Technical Field to order moves')

    @api.depends('state')
    def _compute_is_done(self):
        for move in self:
            move.is_done = (move.state in ('done', 'cancel'))

    def _action_assign(self):
        res = super(StockMove, self)._action_assign()
        for move in self.filtered(lambda x: x.assemble_id or x.pick_assemble_id):
            if move.move_line_ids:
                move.move_line_ids.write({'assemble_id': move.pick_assemble_id.id})
        return res

    def _should_be_assigned(self):
        res = super(StockMove, self)._should_be_assigned()
        flag = bool(res and not (self.assemble_id or self.pick_assemble_id))
        return flag
