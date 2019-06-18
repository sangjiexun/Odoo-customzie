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


class ProductScan(models.Model):
    _name = 'momo.product.scan'
    _description = 'Product Scan'
    _order = 'id'

    picking_id = fields.Many2one('stock.picking', 'Stock Picking')
    picking_name = fields.Char(string="Picking Name", copy=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Stock Picking Type')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    scan = fields.Char(string="Scan", store=False)
    error_mess = fields.Char(string="Error Message")
    linked = fields.Boolean('Linked', default=False)
    product_line_group_id = fields.Many2one('momo.product.line.group', 'Product Line Group', copy=True)

    scan_lines = fields.One2many("momo.product.scan.line", "product_scan_id", copy=True)

    def _get_scan_lines(self):
        self.scan_lines = self.env['momo.product.scan.line'].search(
            [('product_scan_id', '=', self._origin.id)],
            order="create_date desc")

    @api.onchange('scan')
    def _onchange_scan(self):
        picking_id = self.picking_id
        picking_name = self.picking_name
        product_line_group = self.product_line_group_id
        scan_code = self.scan
        self.scan = False
        if scan_code:
            self.update({'error_mess': ' '})
            if (product_line_group.id and product_line_group.useable):
                product_line_link = self.env['momo.product.line.link'].search(['&', ('barcode', '=', scan_code), ('product_line_group_id', '=', product_line_group.id)], limit=1)
            else:
                if(not product_line_group.id):
                    product_line_group = self.env['momo.product.line.group'].create({'group_id': self.picking_id.group_id.id})
                    self.picking_id.write({'product_line_group_id': product_line_group.id})
                    self.update({'product_line_group_id': product_line_group.id})
                product_line_link = self.env['momo.product.line'].search(
                    [('barcode', '=', scan_code)], limit=1)

            if not product_line_link:
                self.update({'error_mess': 'not found this product!'})
            else:
                product_line = self.env['momo.product.line'].search([('barcode', '=', scan_code)], limit=1)
                product_scan_line = self.env['momo.product.scan.line'].search(
                    ['&', ('barcode', '=', scan_code), ('product_scan_id', '=', self._origin.id)], limit=1)
                if product_scan_line:
                    self.update({'error_mess': 'this product has already been scaned!'})
                else:
                    self.env['momo.product.scan.line'].create(
                        {"product_line_id": product_line.id, "location": product_line.current_location,
                         "barcode": scan_code,
                         "product_name": product_line.product_name,
                         "product_id": product_line.product_id.id,
                         "product_scan_id": self._origin.id})
                    line_link = self.env['momo.product.line.link'].search(
                        ['&', ('product_line_group_id', '=', product_line_group.id), ('barcode', '=', scan_code)],
                        order="create_date desc",
                        limit=1)
                    if (line_link):
                        line_link.write({'linked': True})
                    else:
                        self.env['momo.product.line.link'].create(
                            {'product_line_group_id': product_line_group.id, 'product_line_id': product_line.id,
                             'barcode': product_line.barcode, 'product_id': product_line.product_id.id, 'linked': True})

            lines = []
            self._get_scan_lines()

            for rec in self.scan_lines:
                line_item = {
                    'barcode': rec.barcode,
                    'product_name': rec.product_name,
                }
                lines += [line_item]
            self.update({'picking_id': picking_id, 'picking_name': picking_name, 'user_id': self._uid, 'product_line_group_id': self.picking_id.product_line_group_id.id, 'scan_lines': lines})

    @api.onchange('scan_lines')
    def _onchange_active(self):
        picking_id = self.picking_id
        picking_name = self.picking_name
        product_line_group = self.product_line_group_id
        current_view_list = []
        current_db_list = []
        for scan_line in self.scan_lines:
            current_view_list.append(scan_line.barcode)
        db_lines = self.env['momo.product.scan.line'].search([('product_scan_id', '=', self._origin.id)],
                                                             order="create_date desc")
        for scan_line in db_lines:
            current_db_list.append(scan_line.barcode)

        if len(current_db_list) > len(current_view_list):
            self.update({'error_mess': ' '})
            delete_line = list(set(current_db_list).difference(set(current_view_list)))
            if len(delete_line) == 1:
                print("scan id:", self._origin.id)
                print("delete barcode:", delete_line[0])
                print("product_line_group_id:", self.picking_id.product_line_group_id.id)
                self.env['momo.product.scan.line'].search(
                    ['&', ('product_scan_id', '=', self._origin.id), ('barcode', '=', delete_line[0])],
                    order="create_date desc",
                    limit=1).unlink()
                line = self.env['momo.product.line.link'].search(
                    ['&', ('product_line_group_id', '=', self.picking_id.product_line_group_id.id), ('barcode', '=', delete_line[0])],
                    order="create_date desc",
                    limit=1)
                print("deleted line", len(line))
                line.write({'linked': False})
        lines = []
        self._get_scan_lines()

        for rec in self.scan_lines:
            line_item = {
                'barcode': rec.barcode,
                'product_name': rec.product_name,
            }
            lines += [line_item]
        self.update({'picking_id': picking_id, 'picking_name': picking_name, 'user_id': self._uid, 'product_line_group_id': self.picking_id.product_line_group_id.id, 'scan_lines': lines})

    def scan_over(self):
        scan_lines = self.env['momo.product.scan.line'].search([('product_scan_id', '=', self.id)])
        linked_lines = self.env['momo.product.line.link'].search(
            ['&', ('product_line_group_id', '=', self.picking_id.product_line_group_id.id), ('linked', '=', True)])
        scan_lines.unlink()

        for line in linked_lines:
            self.env['momo.product.scan.line'].create(
                {"product_line_id": line.product_line_id.id, "location": line.product_line_id.current_location,
                 "barcode": line.product_line_id.barcode, "product_name": line.product_line_id.product_name,
                 "product_id": line.product_id.id, "product_scan_id": self.id})

            self.env['momo.product.line.picking'].create(
                {"product_line_id": line.product_line_id.id, "stock_picking_id": self.picking_id.id,
                 "barcode": line.product_line_id.barcode})
        scan_line_groups = self.env['momo.product.scan.line'].read_group([('product_scan_id', '=', self.id)], ["id", "product_name"], groupby="product_name")

        for scan_line_group in scan_line_groups:
            product = self.env['product.template'].search([('name', '=', scan_line_group['product_name'])])
            move_line = self.env['stock.move.line'].search(['&', ('picking_id', '=', self.picking_id.id), ('product_id', '=', product.id)])
            move_line.write({'qty_done': int(scan_line_group['product_name_count'])})
        self.picking_id.button_validate()
        self.write({'product_line_group_id': self.picking_id.product_line_group_id.id})
        self.product_line_group_id.write({'useable': True})
        self.picking_id.write({'scan_over': True})
