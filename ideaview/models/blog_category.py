# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import random
import json

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class BlogCategory(models.Model):
    _name = 'idv.blog.category'
    _description = 'Idea View blog category'
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.multi.mixin', 'website.cover_properties.mixin']
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    subtitle = fields.Char('Subtitle', translate=True)
    active = fields.Boolean('Active', default=True)
    content = fields.Html('Content', translate=html_translate, sanitize=False)
    blog_post_ids = fields.One2many('idv.blog', 'category_id', 'Blog Posts')
    blog_post_count = fields.Integer("Posts", compute='_compute_blog_post_count')
    website_url = fields.Char(compute="_compute_website_url")

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = f"/blog/{slug(rec)}"

    @api.depends('blog_post_ids')
    def _compute_blog_post_count(self):
        for record in self:
            record.blog_post_count = len(record.blog_post_ids)
