# -*- coding: utf-8 -*-
from odoo import api, fields, models
import random
import string


class Users(models.Model):
    _inherit = 'res.users'

    # User can write on a few of his own fields (but not his groups for example)
    SELF_WRITEABLE_FIELDS = ['signature', 'action_id', 'company_id', 'user_barcode', 'email', 'name', 'image', 'image_medium', 'image_small', 'lang', 'tz']
    # User can read a few of his own fields
    SELF_READABLE_FIELDS = ['signature', 'company_id', 'login', 'user_barcode', 'email', 'name', 'image', 'image_medium', 'image_small', 'lang', 'tz', 'tz_offset', 'groups_id', 'partner_id', '__last_update', 'action_id']

    user_barcode = fields.Char(help="Used to log into the system by barcode")

    @api.model_create_multi
    def create(self, vals_list):
        users = super(Users, self.with_context(default_customer=False)).create(vals_list)
        for user in users:
            user.update({'user_barcode': self._get_next_user_barcode()})
        return users

    @api.model
    def _get_next_user_barcode(self):
        while True:
            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
            result = self.with_context(active_test=False).search([('user_barcode', '=', random_str)], limit=1)
            if not result:
                break
        return random_str
