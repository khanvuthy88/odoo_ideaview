from datetime import datetime
import random
import json

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class PowerOfReadingCategory(models.Model):
    _name = "idv.power.of.reading.category"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.multi.mixin', 'website.cover_properties.mixin']
    _description = "IDV Power of reading category"
    _order = "name"

    name = fields.Char(required=True)
    active = fields.Boolean('Active', default=True)
    post_ids = fields.One2many("idv.power.of.reading", 'category_id', 'Power of reading posts')
    post_count = fields.Integer("Power of Reading", compute='_compute_post_count')
    website_url = fields.Char(compute="_compute_website_url")

    def _compute_website_url(self):
        for rec in self:
            rec.website_url = f"/power-of-reading-category/{slug(rec)}"

    @api.depends('post_ids')
    def _compute_post_count(self):
        for record in self:
            record.post_count = len(record.post_ids)


class PowerOfReading(models.Model):
    _name = "idv.power.of.reading"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.multi.mixin', 'image.mixin']
    _order = 'name'

    def _compute_website_url(self):
        super(PowerOfReading, self)._compute_website_url()
        for rec in self:
            rec.website_url = "/power-of-reading/%s/%s" % (slug(rec.category_id), slug(rec))

    name = fields.Char(required=True)
    category_id = fields.Many2one('idv.power.of.reading.category')
    short_description = fields.Text()
    active = fields.Boolean(default=True)
    description = fields.Html()

    def _default_website_meta(self):
        res = super(PowerOfReading, self)._default_website_meta()
        res['default_opengraph']['og:description'] = res['default_twitter']['twitter:description'] = self.short_description
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:published_time'] = self.create_date
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:author'] = self.create_uid.sudo().name
        # res['default_opengraph']['article:tag'] = self.tag_ids.mapped('name')
        # background-image might contain single quotes eg `url('/my/url')`
        res['default_opengraph']['og:image'] = res['default_twitter']['twitter:image'] = self.env['website'].image_url(self, 'image_1024')
        res['default_opengraph']['og:title'] = res['default_twitter']['twitter:title'] = self.name
        res['default_meta_description'] = self.short_description
        return res
