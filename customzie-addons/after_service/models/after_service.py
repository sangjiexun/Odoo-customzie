# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from openerp import tools
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

    #saleOrderFilter = fields.Many2one("sale.order",'Sale Order ByNo')
    saleOrderFilter = fields.Many2one("production.line",'Sale Order ByNo')

    order_id = fields.Char('Sale Order Id', readonly=True)
    partner_name = fields.Char('Partner Name', readonly=True)
    barcode = fields.Char('Barcode', index=True, readonly=True)
    defect_remark = fields.Text('Defect Remark', readonly=True)
    treatment_book_id = fields.Many2one(
        "treatment.book", string="Treatment Type")
    treatment_remark = fields.Text(string='Treatment Remark')
    date_approve = fields.Date('Approval Date', readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to processing', 'To Processing'),
        ('to approve', 'To Approve'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', readonly=True, track_visibility='nge')
    claim_note = fields.Text()

    measure_type = fields.Selection(string='Measure Type',selection=[('val1', 'メール'), ('val2', '電話')])
    sale_send_date = fields.Char('Send Date')

    @api.onchange('saleOrderFilter')
    def onchange_saleOrderFilter(self):
        if self.saleOrderFilter:
            self.order_id=self.saleOrderFilter.sale_order_id
            self.partner_name = self.saleOrderFilter.sale_order_partner_id.name
            self.defect_remark = self.saleOrderFilter.defect_remark
            #self.sale_send_date = str((fields.Datetime.today() - self.saleOrderFilter.delivery_date).days + 1) + "日"
            self.sale_send_date = str(21) + "日"
            #self.test_start_date = self.saleOrderFilter.confirmation_date
            #self.test_end_date = fields.Datetime.today()

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
        #############################
        self.write({'state': 'to processing'})

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
