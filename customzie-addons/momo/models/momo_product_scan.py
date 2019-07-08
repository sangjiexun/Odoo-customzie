# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductScanLine(models.Model):
    _name = 'momo.product.scan.line'
    _description = 'Product Scan Line'

    product_scan_id = fields.Many2one('momo.product.scan', 'Product Scan')
    product_line_id = fields.Many2one('momo.product.line', 'Product Line')
    barcode = fields.Char('Barcode')
    location = fields.Char('Location')
    product_name = fields.Char('Product Name')
    product_id = fields.Many2one('product.product', 'Product', index=True, required=True)
    is_defective = fields.Boolean('Is Defective', default=False)
    defective_detail = fields.Text('Defective Detail')


class ProductScan(models.Model):
    _name = 'momo.product.scan'
    _description = 'Product Scan'
    _order = 'id'

    picking_id = fields.Many2one('stock.picking', 'Stock Picking')
    picking_name = fields.Char(string="Picking Name")
    picking_type_id = fields.Many2one('stock.picking.type', 'Stock Picking Type')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    scan_barcode = fields.Char(string="Scan Barcode", store=False)
    error_mess = fields.Char(string="Error Message")
    linked = fields.Boolean('Linked', default=False)
    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group', copy=True)

    scan_lines = fields.One2many("momo.product.scan.line", "product_scan_id", copy=True)

    def _set_scan_screen(self, picking_id):
        self.scan_lines = self.env['momo.product.scan.line'].search(
            [('product_scan_id', '=', self._origin.id)],
            order="create_date desc")
        lines = []
        for scan_line in self.scan_lines:
            line_item = {
                'barcode': scan_line.barcode,
                'product_name': scan_line.product_name,
                'is_defective': scan_line.is_defective,
                'defective_detail': scan_line.defective_detail,
            }
            lines += [line_item]
        picking = self.env['stock.picking'].search([('id', '=', picking_id)], limit=1)
        self.update({'picking_id': picking_id, 'picking_name': picking.name, 'user_id': self._uid,
                     'product_line_group_id': picking.product_line_group_id.id, 'scan_lines': lines})

    @api.onchange('scan_barcode')
    def _onchange_scan_barcode(self):
        self.update({'error_mess': ' '})
        scan_barcode = self.scan_barcode
        picking_id = self.picking_id.id
        self.scan_barcode = False
        if scan_barcode:
            picking = self.env['stock.picking'].search([('id', '=', picking_id)], limit=1)
            if (picking.product_line_group_id.id and picking.product_line_group_id.useable):
                product_line_link = self.env['momo.product.line.link'].search(
                    ['&', ('barcode', '=', scan_barcode),
                     ('product_line_group_id', '=', picking.product_line_group_id.id)],
                    limit=1)
                if not product_line_link:
                    self.update({'error_mess': 'not found this product!'})
                else:
                    product_line = self.env['momo.product.line'].search([('barcode', '=', scan_barcode)], limit=1)
                    product_scan_line = self.env['momo.product.scan.line'].search(
                        ['&', ('barcode', '=', scan_barcode), ('product_scan_id', '=', self._origin.id)], limit=1)
                    if product_scan_line:
                        self.update({'error_mess': 'this product has already been scaned!'})
                    else:
                        self.env['momo.product.scan.line'].create(
                            {"product_line_id": product_line.id, "location": product_line.current_location,
                             "barcode": scan_barcode,
                             "product_name": product_line.product_name,
                             "product_id": product_line.product_id.id,
                             "product_scan_id": self._origin.id})

                        line_link = self.env['momo.product.line.link'].search(
                            ['&', ('product_line_group_id', '=', picking.product_line_group_id.id),
                             ('barcode', '=', scan_barcode)],
                            order="create_date desc",
                            limit=1)
                        if (line_link):
                            line_link.write({'linked': True})
                        else:
                            self.env['momo.product.line.link'].create(
                                {'product_line_group_id': picking.product_line_group_id.id,
                                 'product_line_id': product_line.id,
                                 'barcode': product_line.barcode, 'product_id': product_line.product_id.id,
                                 'linked': True})
            else:
                if (not picking.product_line_group_id.id):
                    product_line_group = self.env['momo.product.line.group'].create(
                        {'group_id': self.picking_id.group_id.id})
                    pickings = self.env['stock.picking'].search([('group_id', '=', picking.group_id.id)])
                    for temp_picking in pickings:
                        temp_picking.write({'product_line_group_id': product_line_group.id})

                product_line = self.env['momo.product.line'].search(
                    [('barcode', '=', scan_barcode)], limit=1)
                if not product_line:
                    self.update({'error_mess': 'not found this product!'})
                else:
                    product_line_move = self.env['stock.move'].search(
                        ['&', ('picking_id', '=', picking.id), ('product_id', '=', product_line.product_id.id)],
                        limit=1)
                    if not product_line_move:
                        self.update({'error_mess': 'wrong product typet!'})
                    else:
                        scaned_qty = self.env['momo.product.scan.line'].search_count(
                            ['&', ('product_name', '=', product_line.product_id.product_tmpl_id.name),
                             ('product_scan_id', '=', self._origin.id)])
                        if scaned_qty >= int(product_line_move.product_qty):
                            self.update({'error_mess': 'this product is enough!'})
                        else:
                            product_scan_line = self.env['momo.product.scan.line'].search(
                                ['&', ('barcode', '=', scan_barcode), ('product_scan_id', '=', self._origin.id)],
                                limit=1)
                            if product_scan_line:
                                self.update({'error_mess': 'this product has already been scaned!'})
                            else:
                                self.env['momo.product.scan.line'].create(
                                    {"product_line_id": product_line.id, "location": product_line.current_location,
                                     "barcode": scan_barcode,
                                     "product_name": product_line.product_name,
                                     "product_id": product_line.product_id.id,
                                     "product_scan_id": self._origin.id})

                                line_link = self.env['momo.product.line.link'].search(
                                    ['&', ('product_line_group_id', '=', picking.product_line_group_id.id),
                                     ('barcode', '=', scan_barcode)],
                                    order="create_date desc",
                                    limit=1)
                                if (line_link):
                                    line_link.write({'linked': True})
                                else:
                                    self.env['momo.product.line.link'].create(
                                        {'product_line_group_id': picking.product_line_group_id.id,
                                         'product_line_id': product_line.id,
                                         'barcode': product_line.barcode, 'product_id': product_line.product_id.id,
                                         'linked': True})
        self._set_scan_screen(picking_id)

    @api.onchange('scan_lines')
    def _onchange_scan_lines(self):
        current_view_list = []
        current_db_list = []
        picking_id = self.picking_id.id
        picking = self.env['stock.picking'].search([('id', '=', picking_id)], limit=1)

        for scan_line in self.scan_lines:
            current_view_list.append(scan_line.barcode)
            self.env['momo.product.scan.line'].search(
                ['&', ('product_scan_id', '=', self._origin.id), ('barcode', '=', scan_line.barcode)], limit=1).write({
                'is_defective': scan_line.is_defective, 'defective_detail': scan_line.defective_detail})
            linked_line = self.env['momo.product.line.link'].search(
                ['&', ('product_line_group_id', '=', picking.product_line_group_id.id),
                 ('barcode', '=', scan_line.barcode)],
                order="create_date desc",
                limit=1)
            linked_line.write({'is_defective': scan_line.is_defective, 'defective_detail': scan_line.defective_detail})

        db_lines = self.env['momo.product.scan.line'].search([('product_scan_id', '=', self._origin.id)],
                                                             order="create_date desc")
        for scan_line in db_lines:
            current_db_list.append(scan_line.barcode)

        if len(current_db_list) > len(current_view_list):
            self.update({'error_mess': ' '})
            delete_line = list(set(current_db_list).difference(set(current_view_list)))
            if len(delete_line) == 1:
                self.env['momo.product.scan.line'].search(
                    ['&', ('product_scan_id', '=', self._origin.id), ('barcode', '=', delete_line[0])],
                    order="create_date desc",
                    limit=1).unlink()
                line = self.env['momo.product.line.link'].search(
                    ['&', ('product_line_group_id', '=', picking.product_line_group_id.id),
                     ('barcode', '=', delete_line[0])],
                    order="create_date desc",
                    limit=1)
                line.write({'linked': False})
        self._set_scan_screen(picking_id)

    def scan_over(self):
        self.env['momo.product.scan.line'].search([('product_scan_id', '=', self.id)]).unlink()
        linked_lines = self.env['momo.product.line.link'].search(
            ['&', ('product_line_group_id', '=', self.picking_id.product_line_group_id.id), ('linked', '=', True)])

        for line in linked_lines:
            self.env['momo.product.scan.line'].create(
                {"product_line_id": line.product_line_id.id, "location": line.product_line_id.current_location,
                 "barcode": line.product_line_id.barcode, "product_name": line.product_line_id.product_name,
                 "product_id": line.product_id.id, "product_scan_id": self.id, 'is_defective': line.is_defective,
                 'defective_detail': line.defective_detail})

            self.env['momo.product.line.picking'].create(
                {"product_line_id": line.product_line_id.id, "stock_picking_id": self.picking_id.id,
                 "barcode": line.product_line_id.barcode})

            self.env['momo.product.line'].search([('barcode', '=', line.product_line_id.barcode)], limit=1).write(
                {'is_defective': line.is_defective, 'defective_detail': line.defective_detail})

        scan_line_groups = self.env['momo.product.scan.line'].read_group(domain=[('product_scan_id', '=', self.id)],
                                                                         fields=["product_id"],
                                                                         groupby="product_id")

        for scan_line_group in scan_line_groups:
            move_line = self.env['stock.move.line'].search(
                ['&', ('picking_id', '=', self.picking_id.id), ('product_id', '=', scan_line_group['product_id'][0])])
            move_line.write({'qty_done': int(scan_line_group['product_id_count'])})
        self.picking_id.button_validate()
        self.write({'product_line_group_id': self.picking_id.product_line_group_id.id})
        self.product_line_group_id.write({'useable': True})
        self.picking_id.write({'scan_over': True})
