# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    only_allowed_products = fields.Boolean(
        string="Use only allowed products in sale")
    allowed_products = fields.Many2many(
        comodel_name='product.product',
        string='Allowed products')

    @api.multi
    def onchange_partner_id(self, partner_id):
        partner_obj = self.env['res.partner']
        result = super(SaleOrder, self).onchange_partner_id(partner_id)
        partner = partner_obj.browse(partner_id)
        result['value']['only_allowed_products'] = partner.sale_only_allowed
        return result

    @api.one
    @api.onchange('only_allowed_products')
    def onchange_only_allowed_products(self):
        supplierinfo_obj = self.env['product.supplierinfo']
        product_obj = self.env['product.product']
        allowed_products = []
        products = product_obj.search([])
        for product in products:
            if product.product_tmpl_id.sale_ok:
                allowed_products.append(product.id)
        self.allowed_products = allowed_products
        allowed_products = []
        if self.only_allowed_products and self.partner_id:
            cond = [('type', '=', 'customer'),
                    ('name', '=', self.partner_id.id)]
            supplierinfo_ids = supplierinfo_obj.search(cond)
            for line in supplierinfo_ids:
                cond = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
                products = product_obj.search(cond)
                allowed_products.extend(products.ids)
            self.allowed_products = [(6, 0, allowed_products)]
