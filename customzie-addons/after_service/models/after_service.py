# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning


class StockMove(models.Model):
    _inherit = 'stock.move'

    after_service_id = fields.Many2one('after.service')


class AfterService(models.Model):
    _name = 'after.service'
    _description = 'After Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'

    name = fields.Char(
        'After Service',
        default=lambda self: self.env['ir.sequence'].next_by_code('after.service'),
        copy=False, required=True, readonly=True)

    saleOrderFilter = fields.Many2one("sale.order",'Sale Order ByNo')

    # Sale
    # production_line_id = fields.Many2one('production.line', string='Production Reference', ondelete='cascade', index=True, copy=False, readonly=True)
    order_id = fields.Char('Sale Order Id', index=True, copy=False, required=True, readonly=False)
    partner_name = fields.Char('Partner Name',index=True, copy=False, required=True, readonly=False)
    # sale_partner_id = fields.Many2one('res.partner', related='production_line_id.sale_partner_id', store=True, string='Customer', readonly=True)
    # sale_move_ids = fields.Many2one('stock.move', related='sale_order_line_id', store=True, string='Sale_Move', readonly=True)
    barcode = fields.Char('Barcode', index=True, readony=True)
    # sale_product_id = fields.Many2one(related='production_line_id.sale_product_id', store=True, string='Order Product', readonly=True)
    # sale_product_no = fields.Many2one('product.product', related='sale_product_id', store=True, string='Sale Product No', readonly=True)
    order_note = fields.Text('Order Note',copy=False, required=True, readonly=False)
    treatment_book_id = fields.Many2one(
        "treatment.book", string="Treatment Type", required=True)
    treatment_remark = fields.Text(string='Treatment Remark')
    date_approve = fields.Date('Approval Date', readonly=True, index=True, copy=False)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to approve', 'To Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='nge')
    move_id = fields.Many2one(
        'stock.move', 'Move',
        copy=False, readonly=True, track_visibility="onchange",
        help="Move created by the After service")

    @api.onchange('saleOrderFilter')
    def onchange_saleOrderFilter(self):
        if self.saleOrderFilter:
            self.order_id=self.saleOrderFilter.name
            self.partner_name = self.saleOrderFilter.partner_id.name
            self.order_note = self.saleOrderFilter.note
            #self.order_amount_total = self.saleOrderFilter.total

    @api.onchange('treatment_book_id')
    def onchange_treatment_book_id(self):
        if self.treatment_book_id:
            self.treatment_remark = self.treatment_book_id.treatment_book

    @api.multi
    def print_after_service(self):
        return self.env.ref('after_service.action_after_service_report').report_action(self)

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
