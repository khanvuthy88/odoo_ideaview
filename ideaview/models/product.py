# -*- coding: utf-8 -*-

from datetime import datetime
import random
import json

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class ProductCategory(models.Model):
    _name = "idv.product.category"
    _inherit = ['website.seo.metadata']
    _description = "IDV Product Category"

    name = fields.Char()
    active = fields.Boolean(default=True)

    product_post_ids = fields.One2many('idv.product', 'category_id', 'Products')
    product_post_count = fields.Integer("Product Count", compute='_compute_product_post_count')
    website_url = fields.Char(compute="_compute_website_url")

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = f"/product/category/{slug(rec)}"

    @api.depends('product_post_ids')
    def _compute_product_post_count(self):
        for record in self:
            record.product_post_count = len(record.product_post_ids)


class Product(models.Model):
    _name = "idv.product"
    _inherit = ['website.seo.metadata', 'image.mixin', 'website.published.multi.mixin']
    _description = "IDV Product"

    def _compute_website_url(self):
        super(Product, self)._compute_website_url()
        for p in self:
            p.website_url = "/product/%s/%s" % (slug(p.category_id), slug(p))

    name = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency', help="Product's currency.",
                                  default=lambda self: self.env.company.currency_id)
    category_id = fields.Many2one('idv.product.category')
    summary_manual = fields.Text()
    summary = fields.Text(compute='_compute_summary')
    price = fields.Monetary(currency_field='currency_id')
    content = fields.Html()
    active = fields.Boolean(default=True)

    @api.depends('content', 'summary_manual')
    def _compute_summary(self):
        for rec in self:
            if rec.summary_manual:
                rec.summary = rec.summary_manual
            else:
                content = html2plaintext(rec.content).replace('\n', ' ')
                rec.summary = content[:200] + '...'

    def _set_summary(self):
        for rec in self:
            rec.summary_manual = rec.summary
