# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = 'stock.rule'
    action = fields.Selection(selection_add=[('assemble', 'Assemble')])

    def _get_message_dict(self):
        message_dict = super(StockRule, self)._get_message_dict()
        source, destination, operation = self._get_message_values()
        assemble_message = _('When products are needed in <b>%s</b>, <br/> a assemble order is created to fulfill the need.') % (destination)
        if self.location_src_id:
            assemble_message += _(' <br/><br/> The components will be taken from <b>%s</b>.') % (source)
        message_dict.update({
            'assemble': assemble_message
        })
        return message_dict

    @api.onchange('action')
    def _onchange_action_operation(self):
        domain = {'picking_type_id': []}
        if self.action == 'assemble':
            domain = {'picking_type_id': [('code', '=', 'assemble_operation')]}
        return {'domain': domain}

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        new_move_vals = super(StockRule, self)._push_prepare_move_copy_values(move_to_copy, new_date)
        new_move_vals['assemble_id'] = False
        return new_move_vals
