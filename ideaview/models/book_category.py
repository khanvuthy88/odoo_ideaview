# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IDVBookCategory(models.Model):
    _name = "idv.book.category"
    _inherit = ['website.seo.metadata']
    _description = 'IDear View Book Category'

    name = fields.Char()
    active = fields.Boolean()
