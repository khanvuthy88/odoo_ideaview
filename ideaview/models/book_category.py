# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug


class IDVBookCategory(models.Model):
    _name = "idv.book.category"
    _inherit = ['website.seo.metadata']
    _description = 'IDear View Book Category'

    name = fields.Char()
    active = fields.Boolean(default=True)

    book_post_ids = fields.One2many('idv.book', 'book_category', 'Book Posts')
    book_post_count = fields.Integer("Posts", compute='_compute_book_post_count')
    website_url = fields.Char(compute="_compute_website_url")

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = f"/book/{slug(rec)}"

    @api.depends('book_post_ids')
    def _compute_book_post_count(self):
        for record in self:
            record.book_post_count = len(record.book_post_ids)
