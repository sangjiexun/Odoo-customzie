# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from openerp import tools
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import Warning

class TreatmentBook(models.Model):
    _name = 'treatment.book'
    _description = 'Treatment Book'
    _order = 'id'

    name = fields.Char('Treatment', required=True, index=True, translate=True)
    treatment_book = fields.Text(string='Treatment Book')

class RepairType(models.Model):
    _name = 'repair.type'
    _description = 'Repair Type'
    _order = 'id'

    name = fields.Char(string='Repiar Type', required=True, index=True, translate=True)

class ProblemReason(models.Model):
    _name = 'problem.reason'
    _description = 'Problem Reason'
    _order = 'id'

    name = fields.Char(string='Problem Reason', required=True, index=True, translate=True)

class AfterService(models.Model):
    _name = 'after.service'
    _description = 'After Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'

    #After Service Reference
    name = fields.Char(string='After Service',required=True, index=True, copy=False, readonly=True, default=lambda self: _('New'))

    #Sale Order Filter
    sale_order_filter = fields.Many2one('momo.product.line', 'Sale Order Filter', required=True)

    #Momo Product Line Id:
    product_line_id = fields.Integer(string='Momo Product Line Id',related='sale_order_filter.id',store=True)

    #Sale Order Id
    sale_order_id = fields.Many2one(string='Sale Order Id',related='sale_order_filter.sale_order_id',store=True)

    #Sale Order Partner Id
    sale_order_partner_id = fields.Char(string='Sale Order Partner Id',related='sale_order_filter.sale_order_name',store=True)

    #Sale Order Product
    sale_order_product = fields.Many2one(string='Sale Order Product', related='sale_order_filter.product_id',store=True)

    #Sale Order Date
    sale_order_date = fields.Datetime(string='Sale Order Date', related='sale_order_filter.delivery_date',store=True)

    #Deficit Price
    deficit_price = fields.Float('Deficit Price', related='sale_order_filter.sale_price_unit',store=True)

    #Inquiry Date
    inquiry_date = fields.Date(string='Inquiry Date',default=fields.Date.today())

    #Contact Person
    contact_person = fields.Many2one('res.users',string='Contact Person', default=lambda self: self.env.user)

    barcode = fields.Char(string='Barcode',related='sale_order_filter.barcode',store=True)

    defect_remark = fields.Text(string='Defect Remark',related='sale_order_filter.defective_detail',store=True)

    #Inquiry Note
    inquiry_note = fields.Text(string='Inquiry Note', required=True)

    #Contact Treatment
    #contact_treatment = fields.Selection(
    #    [('type1','Repairing'),
    #     ('type2','Returned Goods')],
    #    string='Contact Treatment')

    treatment_book_id = fields.Many2one(
        'treatment.book', string='Treatment Type',required=True)

    treatment_remark = fields.Text(string='Treatment Remark')

    #Order Elapsed Days
    order_elapsed_days = fields.Char(sting='Order Elapsed Days', store=True )

    #Returned Date
    returned_date = fields.Date(string='Returned Date',default=fields.Date.today(), required=True, store=True)

    #Reshipping Date
    reshipping_date = fields.Date(string='Reshipping Date',default=fields.Date.today(), required=True, store=True)

    #Repair Type
    repair_type = fields.Many2many('repair.type',string='Repair Type', required=True)

    #Problem Reason
    problem_reason = fields.Many2many('problem.reason',string='Problem Reason')

    #Other Reason                self.write({'deficit_price': self.sale_price_unit})
    other_reason = fields.Text(string='Other Reason')

    #Treatment Operator
    treatment_operator = fields.Many2one('res.users',string='Treatment Operator', default=lambda self: self.env.user)

    #Treatment Date
    treatment_date = fields.Datetime(string='Treatment Date')

    #Company Id
    company_id = fields.Many2one(
            'res.company', 'Company',
            default=lambda self: self.env['res.company']._company_default_get('treatment_operator'))

    date_approve = fields.Date('Approval Date')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('to processing', 'To Processing'),
        ('to approve', 'To Approve'),
        ('done', 'Finshed'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft')

    is_defective = fields.Boolean(string='Is Defective', related='sale_order_filter.is_defective')

    measure_type = fields.Selection(
        [('val1', 'mail'),
        ('val2', 'telephone')],
        string='Measure Type',required=True)

#    @api.multi
#    def show_tree_view(self):
#        self.ensure_one()
#        return {
#            'name': _("Export data"),
#            'view_type': 'form',
#            'view_mode': 'tree',
#            'res_model': self.model,
#            'view_id': False,
#            'type': 'ir.actions.act_window',
#            'context': self.env.context,
#        }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('after.service') or _('New')
        return super(AfterService, self).create(vals)

    @api.onchange('sale_order_filter')
    def onchange_sale_order_filter(self):
        if self.sale_order_filter:
            if not self.sale_order_filter.delivery_date:
                self.order_elapsed_days = ''
            else:
                self.order_elapsed_days = str((fields.Datetime.today() - self.sale_order_filter.delivery_date).days + 1) + '日'
            self.is_defective = self.sale_order_filter.is_defective

    @api.onchange('treatment_book_id')
    def onchange_treatment_book_id(self):
        if self.treatment_book_id:
            self.treatment_remark = self.treatment_book_id.treatment_book

    @api.multi
    def print_after_service(self):
        return self.env.ref('after_service.action_after_service_report').report_action(self)

    @api.multi
    def button_draft(self):
        if not self.measure_type:
            raise UserError(_("Please select an inquiry method."))
        else:
            if not self.treatment_book_id:
                raise UserError(_("Please enter treatment category."))
            else:
                self.write({'state': 'draft'})
                self.write({'sale_order_id': self.sale_order_id})
                self.write({'sale_order_partner_id': self.sale_order_partner_id})
                self.write({'sale_order_date': self.sale_order_date})
                self.write({'deficit_price': self.sale_price_unit})
                self.write({'defect_remark': self.defect_remark})
                self.write({'order_elapsed_days': self.order_elapsed_days})
                self.write({'barcode': self.barcode})
                self.write({'inquiry_note': self.inquiry_note})
        return {}

    @api.multi
    def button_processing(self, force=False):
        if not self.repair_type:
            raise UserError(_("Please enter the corresponding content."))
        else:
            self.write({'treatment_operator': self.env.uid})
            self.write({'treatment_date': datetime.now()})
            self.write({'is_defective': self.is_defective})
            if self.is_defective:
                self.write({'state': 'to approve'})
            else:
                self.write({'state': 'done', 'date_approve': fields.Date.context_today(self)})
        return {}

    @api.multi
    def button_approve(self, force=False):
        self.write({'state': 'done', 'date_approve': fields.Date.context_today(self)})
        return {}

    @api.multi
    def button_confirm(self):
        self.write({'state': 'to processing'})
        return {}

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancel'})
        return {}
