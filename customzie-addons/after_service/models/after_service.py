# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning


class StockMove(models.Model):
    _inherit = 'stock.move'

    after_service_id = fields.Many2one('after.service')


class AfterService(models.Model):
    _name = 'after.service'
    _description = 'After Service'
    _order = 'id'

    name = fields.Char(
        'After Service',
        default=lambda self: self.env['ir.sequence'].next_by_code('after.service'),
        copy=False, required=True, readonly=True)

    # Sale
    # production_line_id = fields.Many2one('production.line', string='Production Reference', ondelete='cascade', index=True, copy=False, readonly=True)
    order_id = fields.Char('Sale Order', index=True, readony=True)
    # sale_partner_id = fields.Many2one('res.partner', related='production_line_id.sale_partner_id', store=True, string='Customer', readonly=True)
    # sale_move_ids = fields.Many2one('stock.move', related='sale_order_line_id', store=True, string='Sale_Move', readonly=True)
    barcode = fields.Char('Barcode', index=True, readony=True)
    # sale_product_id = fields.Many2one(related='production_line_id.sale_product_id', store=True, string='Order Product', readonly=True)
    # sale_product_no = fields.Many2one('product.product', related='sale_product_id', store=True, string='Sale Product No', readonly=True)
    treatment_book_id = fields.Many2one(
        "treatment.book", string="Treatment Type", required=True)
    treatment_remark = fields.Text(string='Treatment Remark')
    date_approve = fields.Date('Approval Date', readonly=True, index=True, copy=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to approve', 'To Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='onchange')
    move_id = fields.Many2one(
        'stock.move', 'Move',
        copy=False, readonly=True, track_visibility="onchange",
        help="Move created by the After service")

    @api.onchange('treatment_book_id')
    def onchange_treatment_book_id(self):
        if self.treatment_book_id:
            self.treatment_remark = self.treatment_book_id.treatment_book

    @api.multi
    def print_after_service(self):
        return self.env.ref('after_service.action_report_after_service').report_action(self)

    @api.multi
    def button_approve(self, force=False):
        self.write({'state': 'done', 'date_approve': fields.Date.context_today(self)})
        return {}

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    @api.multi
    def button_confirm(self):
        self.write({'state': 'to approve'})
        return {}

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return {}


class TreatmentBook(models.Model):
    _name = 'treatment.book'
    _description = 'Treatment Book'
    _order = 'id'

    name = fields.Char('Treatment', required=True, index=True, translate=True)
    treatment_book = fields.Text(string='Treatment Book')
