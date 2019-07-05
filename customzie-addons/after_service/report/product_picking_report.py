# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ProductionReport(models.Model):
    _name = "momo.production.picking.report"
    _description = 'Production Picking / Report'
    _auto = False
    _order = "create_date DESC"

    product_line_id = fields.Many2one('momo.product.line', 'Product Line', readonly=True)
    barcode = fields.Char('Barcode')
    picking_type_name = fields.Char('Picking Type Name', readonly=True)
    create_uid = fields.Many2one('res.users', string="User", readonly=True)
    create_date = fields.Datetime('Create Date', readonly=True)


    def init(self):
        tools.drop_view_if_exists(self._cr, 'momo_production_picking_report')

        self._cr.execute("""
            CREATE or REPLACE view momo_production_picking_report as (
            SELECT row_number() OVER(Order by picking.create_date asc) as id,
                picking.product_line_id as product_line_id,
                picking.barcode as barcode,
                picking.picking_type_id_name as picking_type_name,
                picking.create_uid as create_uid,
                picking.create_date as create_date
            from momo_product_line_picking as picking
            union all select
                row_number()  OVER(Order by clean.create_date asc) as id,
                clean.product_line_id as product_line_id,
                clean.barcode as barcode,
                'Clean' as picking_type_name,
                clean.create_uid as create_uid,
                clean.create_date as create_date
            from momo_product_clean_history as clean
            union all select
                row_number()  OVER(Order by officer.create_date asc) as id,
                officer.product_line_id as product_line_id,
                officer.barcode as barcode,
            CASE officer.measure_type
                WHEN 'val1' THEN 'Mail'
                WHEN 'val2' THEN 'Tel'
                ELSE 'Other'
            END as picking_type_name,
                officer.create_uid as create_uid,
                officer.create_date as create_date
            from after_service as officer
            union all select
                row_number()  OVER(Order by operator.create_date asc) as id,
                operator.product_line_id as product_line_id,
                operator.barcode as barcode,
                'repair' as picking_type_name,
                operator.treatment_operator as create_uid,
                operator.treatment_date as create_date
            from after_service as operator
            );
        """)