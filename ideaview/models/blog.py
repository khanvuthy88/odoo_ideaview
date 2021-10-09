# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import random
import json

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class BlogPost(models.Model):
    _name = "idv.blog"
    _description = "Idea view Blog Post"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.multi.mixin',
                'website.cover_properties.mixin', 'image.mixin']
    _order = 'id DESC'
    _mail_post_access = 'read'

    def _compute_website_url(self):
        super(BlogPost, self)._compute_website_url()
        for blog_post in self:
            blog_post.website_url = "/blog/%s/%s" % (slug(blog_post.category_id), slug(blog_post))

    def _default_content(self):
        return '''
            <p class="o_default_snippet_text">''' + _("Start writing here...") + '''</p>
        '''

    name = fields.Char('Title', required=True, translate=True, default='')
    author_id = fields.Many2one('res.partner', 'Author', default=lambda self: self.env.user.partner_id)
    author_avatar = fields.Binary(related='author_id.image_128', string="Avatar", readonly=False)
    author_name = fields.Char(related='author_id.display_name', string="Author Name", readonly=False, store=True)
    active = fields.Boolean('Active', default=True)
    category_id = fields.Many2one('idv.blog.category', 'Category', required=True, ondelete='cascade')
    content = fields.Html('Content', default=_default_content, translate=html_translate, sanitize=False)
    teaser = fields.Text('Teaser', compute='_compute_teaser', inverse='_set_teaser')
    teaser_manual = fields.Text(string='Teaser Content')

    website_message_ids = fields.One2many(
        domain=lambda self: [('model', '=', self._name), ('message_type', '=', 'comment')])
    visits = fields.Integer('No of Views', copy=False, default=0)
    website_id = fields.Many2one(related='category_id.website_id', readonly=True, store=True)

    @api.depends('content', 'teaser_manual')
    def _compute_teaser(self):
        for blog_post in self:
            if blog_post.teaser_manual:
                blog_post.teaser = blog_post.teaser_manual
            else:
                content = html2plaintext(blog_post.content).replace('\n', ' ')
                blog_post.teaser = content[:115] + '...'

    def _set_teaser(self):
        for blog_post in self:
            blog_post.teaser_manual = blog_post.teaser

    def _default_website_meta(self):
        res = super(BlogPost, self)._default_website_meta()
        res['default_opengraph']['og:description'] = res['default_twitter']['twitter:description'] = self.teaser
        res['default_opengraph']['og:type'] = 'article'
        res['default_opengraph']['article:published_time'] = self.create_date
        res['default_opengraph']['article:modified_time'] = self.write_date
        res['default_opengraph']['article:author'] = self.author_id.sudo().name
        # res['default_opengraph']['article:tag'] = self.tag_ids.mapped('name')
        # background-image might contain single quotes eg `url('/my/url')`
        res['default_opengraph']['og:image'] = res['default_twitter']['twitter:image'] = self.env['website'].image_url(self, 'image_1024')
        res['default_opengraph']['og:title'] = res['default_twitter']['twitter:title'] = self.name
        res['default_meta_description'] = self.teaser
        return res