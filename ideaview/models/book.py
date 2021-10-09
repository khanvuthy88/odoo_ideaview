# -*- coding: utf-8 -*-

from datetime import datetime
import random
import json

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class IDVBook(models.Model):
    _name = "idv.book"
    _inherit = ['website.seo.metadata', 'image.mixin', 'website.published.multi.mixin']
    _order = 'name'
    _description = "IDear View Book"

    def _compute_website_url(self):
        super(IDVBook, self)._compute_website_url()
        for book in self:
            book.website_url = "/book/%s/%s" % (slug(book.book_category), slug(book))

    name = fields.Char(required=True)
    description = fields.Html()
    currency_id = fields.Many2one('res.currency', string='Currency', help="Book's currency.", default=lambda self: self.env.company.currency_id)
    author_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    price = fields.Monetary(currency_field='currency_id')
    book_size = fields.Char()
    book_isbn = fields.Char()
    number_of_pages = fields.Integer()
    book_category = fields.Many2one('idv.book.category')
    audio_file = fields.Binary()
    active = fields.Boolean(default=True)
    teaser_manual = fields.Text(string='Teaser Content')
    teaser = fields.Text('Teaser', compute='_compute_teaser', inverse='_set_teaser')

    @api.depends('description', 'teaser_manual')
    def _compute_teaser(self):
        for rec in self:
            if rec.teaser_manual:
                rec.teaser = rec.teaser_manual
            else:
                content = html2plaintext(rec.description).replace('\n', ' ')
                rec.teaser = content[:200] + '...'

    def _set_teaser(self):
        for rec in self:
            rec.teaser_manual = rec.teaser


