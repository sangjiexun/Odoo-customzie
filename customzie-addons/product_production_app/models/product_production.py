# -*- coding: utf-8 -*-
from odoo import api,fields, models
from odoo.exceptions import Warning

class ProductProduction(models.Model):
    _name = 'product.production' #モデル名
    _description = 'Product Prodtuction' #説明
    barcode = fields.Char('製品バーコード',size=13) #product_no+serial_no
    name = fields.Char('Name') 
    product_no = fields.Char('製品番号') 
    purchase_order_name  = fields.Char('購買オーダ名') 
    repair_order_name  = fields.Char('修理オーダ名') 
    sale_order_name  = fields.Char('販売オーダ名') 
    serial_no  = fields.Char('製品シリアル番号') 
    stock_status  = fields.Integer('在庫状態') #0：入荷 1：在庫 2：出庫 3：出荷 4：廃棄
    stock_status_child  = fields.Integer('在庫状態(その他)') #返品､製造､梱包､清掃､修理
    remark  = fields.Char('備考') #備考 メモ
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
