# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('assem_operation', 'Assemble Operation')])
    count_as_todo = fields.Integer(string="Number of Assemble Orders to Process",
        compute='_get_as_count')
    count_as_waiting = fields.Integer(string="Number of Assemble Orders Waiting",
        compute='_get_as_count')
    count_as_late = fields.Integer(string="Number of Assemble Orders Late",
        compute='_get_as_count')

    def _get_as_count(self):
        assemble_picking_types = self.filtered(lambda picking: picking.code == 'assemble_operation')
        if not assemble_picking_types:
            return
        domains = {
            'count_as_waiting': [('availability', '=', 'waiting')],
            'count_as_todo': [('state', 'in', ('confirmed', 'planned', 'progress'))],
            'count_as_late': [('date_planned_start', '<', fields.Date.today()), ('state', '=', 'confirmed')],
        }
        for field in domains:
            data = self.env['nashi.assemble'].read_group(domains[field] +
                [('state', 'not in', ('done', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {x['picking_type_id'] and x['picking_type_id'][0]: x['picking_type_id_count'] for x in data}
            for record in assemble_picking_types:
                record[field] = count.get(record.id, 0)

    def get_assemble_stock_picking_action_picking_type(self):
        return self._get_action('mrp.mrp_production_action_picking_deshboard')
