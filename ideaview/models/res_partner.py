# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug, slugify, _guess_mimetype


class ResPartner(models.Model):
    _inherit = 'res.partner'

    book_author = fields.Boolean()
    blog_post_ids = fields.One2many('idv.blog', 'author_id', 'Blog Posts')
    blog_post_count = fields.Integer("Posts", compute='_compute_blog_post_count')

    book_post_ids = fields.One2many('idv.book', 'author_id')
    book_post_count = fields.Integer('Books', compute="_compute_book_post_count")
    book_website_url = fields.Char(compute="_compute_blog_author_website_url")
    author_website_url = fields.Char(compute="_compute_blog_author_website_url")

    @api.depends('book_post_ids')
    def _compute_book_post_count(self):
        for rec in self:
            rec.book_post_count = len(rec.book_post_ids)

    @api.depends('blog_post_ids')
    def _compute_blog_post_count(self):
        for record in self:
            record.blog_post_count = len(record.blog_post_ids)

    def _compute_blog_author_website_url(self):
        for rec in self:
            rec.book_website_url = f'/book/author/{slug(rec)}'
            rec.author_website_url = f'/blog/author/{slug(rec)}'
