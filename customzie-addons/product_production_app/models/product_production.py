# -*- coding: utf-8 -*-
from odoo import api,fields, models
from odoo.exceptions import Warning

class ProductProduction(models.Model):
    _name = 'product.production' #モデル名
    _description = 'Product Prodtuction' #説明
    barcode = fields.Char('barcode',size=13,readonly=True) #product_no+serial_no
    name = fields.Char('Name') 
    product_no = fields.Char('Product No',readonly=True) 
    purchase_order_name  = fields.Char('Purchase Order Name',readonly=True) 
    repair_order_name  = fields.Char('Repair Order Name',readonly=True) 
    sale_order_name  = fields.Char('Sale Order Name',readonly=True) 
    serial_no  = fields.Char('Serial No',readonly=True) 
    stock_status  = fields.Integer('Stock Status') #0：入荷 1：在庫 2：出庫 3：出荷 4：廃棄
    stock_status_child  = fields.Integer('Stock Status Child') #返品､製造､梱包､清掃､修理
    product_status  = fields.Selection([
        ('0', '正常'),
        ('1', '瑕疵品(可用)'),
        ('2', '瑕疵品(作废)'),
        ('3', '瑕疵品(その他)'),
    ], default='0', string='Product Status')
    remark  = fields.Text('Remark') #備考 メモ
    #scan_barcode event
    def onchange_scan_barcode(self):
        return True
    #印刷
    def button_print(self):
        #for book in self:
         #   if not book.isbn:
          #      raise Warningg('Please provide an ISBN for %s' % book.name)
           # if book.isbn and not book._check_isbn():
            #    raise Warning('%s is an invalid ISBN' % book.isbn)
        return True
    #増加
    def button_insert(self):
        # serial_no 参考例
        # param = (env['ir.sequence'].next_by_code('dycrm.cwbh'),record.id)
        #保存的时候根据record.id当前记录的id值，更新表的cwbh字段
        # env.cr.execute("update dycrm_main set cwbh=%s where id=%s"% param)
        
        # barcode処理追加
        # barcode = product_no+serial_no
        #for book in self:
         #   if not book.isbn:
          #      raise Warningg('Please provide an ISBN for %s' % book.name)
           # if book.isbn and not book._check_isbn():
            #    raise Warning('%s is an invalid ISBN' % book.isbn)
        return True
    #更新
    def button_update(self):
        #for book in self:
         #   if not book.isbn:
          #      raise Warningg('Please provide an ISBN for %s' % book.name)
           # if book.isbn and not book._check_isbn():
            #    raise Warning('%s is an invalid ISBN' % book.isbn)
        return True
    #検索
    def button_search(self):
        #for book in self:
         #   if not book.isbn:
          #      raise Warningg('Please provide an ISBN for %s' % book.name)
           # if book.isbn and not book._check_isbn():
            #    raise Warning('%s is an invalid ISBN' % book.isbn)
        return True
    def button_input_individual(self):
        #個別入庫画面に遷移
        return True
    def button_input_batch(self):
        #バッチ入庫画面に遷移
        return True
    def button_input_confrim(self):
        #入庫画面の｢入庫｣ボタンの対応
        return True
