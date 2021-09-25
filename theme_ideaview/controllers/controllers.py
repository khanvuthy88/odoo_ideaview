# -*- coding: utf-8 -*-
# from odoo import http


# class ThemeIdeaview(http.Controller):
#     @http.route('/theme_ideaview/theme_ideaview/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/theme_ideaview/theme_ideaview/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('theme_ideaview.listing', {
#             'root': '/theme_ideaview/theme_ideaview',
#             'objects': http.request.env['theme_ideaview.theme_ideaview'].search([]),
#         })

#     @http.route('/theme_ideaview/theme_ideaview/objects/<model("theme_ideaview.theme_ideaview"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('theme_ideaview.object', {
#             'object': obj
#         })
