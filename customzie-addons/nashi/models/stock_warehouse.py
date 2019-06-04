# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    assemble_to_resupply = fields.Boolean(
        'Assemble to Resupply', default=True,
        help="When products are asembled, they can be asembled in this warehouse.")
    assemble_pull_id = fields.Many2one(
        'stock.rule', 'Asemble Rule')
    pba_mto_pull_id = fields.Many2one(
        'stock.rule', 'Picking Before Asemble MTO Rule')
    saa_rule_id = fields.Many2one(
        'stock.rule', 'Stock After Asemble Rule')

    assem_type_id = fields.Many2one(
        'stock.picking.type', 'Assemble Operation Type',
        domain=[('code', '=', 'assem_operation')])

    pba_type_id = fields.Many2one('stock.picking.type', 'Picking Before Assemble Operation Type')
    saa_type_id = fields.Many2one('stock.picking.type', 'Stock After Assemble Operation Type')

    assemble_steps = fields.Selection([
        ('pba_saa', 'Pick components, manufacture and then store products (3 steps)')],
        'Assemble', default='pba_saa', required=True)

    pba_route_id = fields.Many2one('stock.location.route', 'Picking Before Assemble Route', ondelete='restrict')

    pba_loc_id = fields.Many2one('stock.location', 'Picking before Assemble Location')
    saa_loc_id = fields.Many2one('stock.location', 'Stock after Assemble Location')

    def get_rules_dict(self):
        result = super(StockWarehouse, self).get_rules_dict()
        assemble_location_id = self._get_assemble_location()
        for warehouse in self:
            result[warehouse.id].update({
                'pba_saa': [
                    self.Routing(warehouse.lot_stock_id, warehouse.pba_loc_id, warehouse.pba_type_id, 'pull'),
                    self.Routing(warehouse.pba_loc_id, assemble_location_id, warehouse.assem_type_id, 'pull'),
                    self.Routing(warehouse.saa_loc_id, warehouse.lot_stock_id, warehouse.saa_type_id, 'push'),
                ],
            })
        return result

    @api.model
    def _get_assemble_location(self):
        location = self.env['stock.location'].search([('usage', '=', 'assemble')], limit=1)
        if not location:
            raise UserError(_('Can\'t find any assemble location.'))
        return location

    def _get_routes_values(self):
        routes = super(StockWarehouse, self)._get_routes_values()
        routes.update({
            'pba_route_id': {
                'routing_key': self.assemble_steps,
                'depends': ['assemble_steps', 'assemble_to_resupply'],
                'route_update_values': {
                    'name': self._format_routename(route_type=self.assemble_steps),
                    'active': self.assemble_steps != '',
                },
                'route_create_values': {
                    'product_categ_selectable': True,
                    'warehouse_selectable': True,
                    'product_selectable': False,
                    'company_id': self.company_id.id,
                    'sequence': 10,
                },
                'rules_values': {
                    'active': True,
                }
            }
        })
        return routes

    def _get_route_name(self, route_type):
        names = {
            'pba_saa': _('Pick products, assemble and then store products (3 steps)'),
        }
        if route_type in names:
            return names[route_type]
        else:
            return super(StockWarehouse, self)._get_route_name(route_type)

    def _get_global_route_rules_values(self):
        rules = super(StockWarehouse, self)._get_global_route_rules_values()
        location_id = self.assemble_steps == 'pba_saa' and self.saa_loc_id or self.lot_stock_id
        rules.update({
            'assemble_pull_id': {
                'depends': ['assemble_steps', 'assemble_to_resupply'],
                'create_values': {
                    'action': 'assemble',
                    'procure_method': 'make_to_order',
                    'company_id': self.company_id.id,
                    'picking_type_id': self.assem_type_id.id,
                    'route_id': self._find_global_route('nashi.route_warehouse0_assemble', _('Assemble')).id
                },
                'update_values': {
                    'active': self.assemble_to_resupply,
                    'name': self._format_rulename(location_id, False, 'Assemble'),
                    'location_id': location_id.id,
                }
            },
            'pba_mto_pull_id': {
                'depends': ['assemble_steps', 'assemble_to_resupply'],
                'create_values': {
                    'procure_method': 'make_to_order',
                    'company_id': self.company_id.id,
                    'action': 'pull',
                    'auto': 'manual',
                    'propagate': True,
                    'route_id': self._find_global_route('stock.route_warehouse0_mto', _('Make To Order')).id,
                    'name': self._format_rulename(self.lot_stock_id, self.pba_loc_id, 'MTO'),
                    'location_id': self.pba_loc_id.id,
                    'location_src_id': self.lot_stock_id.id,
                    'picking_type_id': self.pba_type_id.id
                },
                'update_values': {
                    'active': self.assemble_steps != '' and self.assemble_to_resupply,
                }
            },
            # The purpose to move sam rule in the manufacture route instead of
            # pbm_route_id is to avoid conflict with receipt in multiple
            # step. For example if the product is manufacture and receipt in two
            # step it would conflict in WH/Stock since product could come from
            # WH/post-prod or WH/input. We do not have this conflict with
            # manufacture route since it is set on the product.
            'saa_rule_id': {
                'depends': ['assemble_steps', 'assemble_to_resupply'],
                'create_values': {
                    'procure_method': 'make_to_order',
                    'company_id': self.company_id.id,
                    'action': 'pull',
                    'auto': 'manual',
                    'propagate': True,
                    'route_id': self._find_global_route('nashi.route_warehouse0_assemble', _('Assemble')).id,
                    'name': self._format_rulename(self.saa_loc_id, self.lot_stock_id, False),
                    'location_id': self.lot_stock_id.id,
                    'location_src_id': self.saa_loc_id.id,
                    'picking_type_id': self.saa_type_id.id
                },
                'update_values': {
                    'active': self.assemble_steps == 'pba_saa' and self.assemble_to_resupply,
                }
            }

        })
        return rules

    def _get_locations_values(self, vals):
        values = super(StockWarehouse, self)._get_locations_values(vals)
        def_values = self.default_get(['assemble_steps'])
        assemble_steps = vals.get('assemble_steps', def_values['assemble_steps'])
        code = vals.get('code') or self.code
        code = code.replace(' ', '').upper()
        values.update({
            'pba_loc_id': {
                'name': _('Pre-Assemble'),
                'active': assemble_steps in ('pba_saa'),
                'usage': 'internal',
                'barcode': code + '-PREASSEMBLE'
            },
            'saa_loc_id': {
                'name': _('Post-Assemble'),
                'active': assemble_steps == 'pba_saa',
                'usage': 'internal',
                'barcode': code + '-POSTASSEMBLE'
            },
        })
        return values

    def _get_sequence_values(self):
        values = super(StockWarehouse, self)._get_sequence_values()
        values.update({
            'pba_type_id': {'name': self.name + ' ' + _('Sequence picking before assemble'), 'prefix': self.code + '/PBA/', 'padding': 5},
            'saa_type_id': {'name': self.name + ' ' + _('Sequence stock after assemble'), 'prefix': self.code + '/SAA/', 'padding': 5},
            'assem_type_id': {'name': self.name + ' ' + _('Sequence assemble'), 'prefix': self.code + '/AS/', 'padding': 5},
        })
        return values

    def _get_picking_type_create_values(self, max_sequence):
        data, next_sequence = super(StockWarehouse, self)._get_picking_type_create_values(max_sequence)
        data.update({
            'pba_type_id': {
                'name': _('Pick Products'),
                'code': 'internal',
                'use_create_lots': True,
                'use_existing_lots': True,
                'default_location_src_id': self.lot_stock_id.id,
                'default_location_dest_id': self.pba_loc_id.id,
                'sequence': next_sequence + 1
            },
            'saa_type_id': {
                'name': _('Store Finished Products'),
                'code': 'internal',
                'use_create_lots': True,
                'use_existing_lots': True,
                'default_location_src_id': self.saa_loc_id.id,
                'default_location_dest_id': self.lot_stock_id.id,
                'sequence': next_sequence + 3
            },
            'assem_type_id': {
                'name': _('Assemble'),
                'code': 'assem_operation',
                'use_create_lots': True,
                'use_existing_lots': True,
                'sequence': next_sequence + 2
            },
        })
        return data, max_sequence + 4

    def _get_picking_type_update_values(self):
        data = super(StockWarehouse, self)._get_picking_type_update_values()
        data.update({
            'pba_type_id': {'active': self.assemble_to_resupply and self.assemble_steps in ('pba_saa')},
            'saa_type_id': {'active': self.assemble_to_resupply and self.assemble_steps == 'pba_saa'},
            'assem_type_id': {
                'active': self.assemble_to_resupply,
                'default_location_src_id': self.assemble_steps in ('pba_saa') and self.pba_loc_id.id or self.lot_stock_id.id,
                'default_location_dest_id': self.assemble_steps == 'pba_saa' and self.saa_loc_id.id or self.lot_stock_id.id,
            },
        })
        return data

    @api.multi
    def write(self, vals):
        if any(field in vals for field in ('assemble_steps', 'assemble_to_resupply')):
            for warehouse in self:
                warehouse._update_location_assemble(vals.get('assemble_steps', warehouse.assemble_steps))
        return super(StockWarehouse, self).write(vals)

    @api.multi
    def _get_all_routes(self):
        routes = super(StockWarehouse, self).get_all_routes_for_wh()
        routes |= self.filtered(lambda self: self.assemble_to_resupply and self.assemble_pull_id and self.assemble_pull_id.route_id).mapped('assemble_pull_id').mapped('route_id')
        return routes

    def _update_location_assemble(self, new_assemble_steps):
        switch_warehouses = self.filtered(lambda wh: wh.assemble_steps != new_assemble_steps)
        loc_warehouse = switch_warehouses.filtered(lambda wh: not wh._location_used(wh.pba_loc_id))
        if loc_warehouse:
            loc_warehouse.mapped('pba_loc_id').write({'active': False})
        loc_warehouse = switch_warehouses.filtered(lambda wh: not wh._location_used(wh.saa_loc_id))
        if loc_warehouse:
            loc_warehouse.mapped('saa_loc_id').write({'active': False})
        if new_assemble_steps != '':
            self.mapped('pba_loc_id').write({'active': True})
        if new_assemble_steps == 'pba_saa':
            self.mapped('saa_loc_id').write({'active': True})

    @api.multi
    def _update_name_and_code(self, name=False, code=False):
        res = super(StockWarehouse, self)._update_name_and_code(name, code)
        # change the manufacture stock rule name
        for warehouse in self:
            if warehouse.assemble_pull_id and name:
                warehouse.assemble_pull_id.write({'name': warehouse.assemble_pull_id.name.replace(warehouse.name, name, 1)})
        return res
