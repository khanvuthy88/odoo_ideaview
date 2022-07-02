# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Website(models.Model):
    _inherit = "website"

    website_banner = fields.Image()
