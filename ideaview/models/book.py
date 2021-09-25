# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug, slugify, _guess_mimetype


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
    currency_id = fields.Many2one('res.currency')
    author_id = fields.Many2one('res.partner', default=lambda self: self.env.user.partner_id)
    price = fields.Float()
    book_size = fields.Char()
    book_isbn = fields.Char()
    number_of_pages = fields.Integer()
    book_category = fields.Many2one('idv.book.category')
    audio_file = fields.Binary()
    active = fields.Boolean(default=True)


