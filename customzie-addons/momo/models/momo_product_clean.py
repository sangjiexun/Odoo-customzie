# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductCleanHistory(models.Model):
    _name = 'momo.product.clean.history'
    _description = 'Product Clean History'

    product_clean_id = fields.Many2one('momo.product.clean', 'Product Clean', index=True, required=True)
    product_line_id = fields.Many2one('momo.product.line', 'Product Line', index=True, required=True)
    barcode = fields.Char('Barcode')
    location = fields.Char('Location')
    product_name = fields.Char('Product Name')


class ProductClean(models.Model):
    _name = 'momo.product.clean'
    _description = 'Product Clean'
    _order = 'id'

    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    scan = fields.Char(string="Scan", store=False)
    error_mess = fields.Char(string="Error Message")

    clean_history_ids = fields.One2many("momo.product.clean.history", "product_line_id", copy=True)

    def _get_clean_history_ids(self):
        self.clean_history_ids = self.env['momo.product.clean.history'].search(
            [('product_clean_id', '=', self._origin.id)],
            order="create_date desc")

    @api.onchange('scan')
    def _onchange_scan(self):
        scan_code = self.scan
        self.scan = False
        if scan_code:
            self.update({'error_mess': ' '})
            product_line = self.env['momo.product.line'].search([('barcode', '=', scan_code)], limit=1)
            if not product_line:
                self.update({'error_mess': 'not found this product!'})
            else:
                if not product_line.need_clean:
                    self.update({'error_mess': 'this product do not need to clean!'})
                else:
                    product_clean_history = self.env['momo.product.clean.history'].search(
                        ['&', ('barcode', '=', scan_code), ('product_clean_id', '=', self._origin.id)], limit=1)
                    if product_clean_history:
                        self.update({'error_mess': 'this product has already been cleaned!'})
                    else:
                        self.env['momo.product.clean.history'].create(
                            {"product_line_id": product_line.id, "location": product_line.current_location,
                             "barcode": scan_code, "product_name": product_line.product_name,
                             "product_clean_id": self._origin.id})
                        product_line.write({'is_cleaned': True})

            lines = []
            self._get_clean_history_ids()

            for rec in self.clean_history_ids:
                line_item = {
                    'barcode': rec.barcode,
                    'product_name': rec.product_name,
                }
                lines += [line_item]

            self.update({'user_id': self._uid, 'clean_history_ids': lines})

    @api.onchange('clean_history_ids')
    def _onchange_active(self):
        current_view_list = []
        current_db_list = []

        for clean_history_id in self.clean_history_ids:
            current_view_list.append(clean_history_id.barcode)

        db_lines = self.env['momo.product.clean.history'].search([('product_clean_id', '=', self._origin.id)],
                                                                 order="create_date desc")
        for clean_history_id in db_lines:
            current_db_list.append(clean_history_id.barcode)

        if len(current_db_list) > len(current_view_list):
            self.update({'error_mess': ' '})
            delete_line = list(set(current_db_list).difference(set(current_view_list)))

            if len(delete_line) == 1:
                self.env['momo.product.clean.history'].search(
                    ['&', ('product_clean_id', '=', self._origin.id), ('barcode', '=', delete_line[0])],
                    order="create_date desc",
                    limit=1).unlink()

            lines = []
            self._get_clean_history_ids()

            for rec in self.clean_history_ids:
                line_item = {
                    'barcode': rec.barcode,
                    'product_name': rec.product_name,
                }
                lines += [line_item]
            self.update({'user_id': self._uid, 'clean_history_ids': lines})
