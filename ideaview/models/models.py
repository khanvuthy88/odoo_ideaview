# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IDVBookCategory(models.Model):
    _name = "idv.book.category"
    _inherit = ['website.seo.metadata']
    _description = 'IDear View Book Category'

    name = fields.Char()
    active = fields.Boolean()


class IDVBook(models.Model):
    _name = "idv.book"
    _inherit = ['website.seo.metadata', 'image.mixin']
    _order = 'name'
    _description = "IDear View Book"

    name = fields.Char()
    description = fields.Text()
    author_id = fields.Many2one('res.partner')
    price = fields.Float()
    book_size = fields.Char()
    book_isbn = fields.Char()
    number_of_pages = fields.Integer()
    book_category = fields.Many2one('idv.book.category')
    audio_file = fields.Binary()
    active = fields.Boolean()

