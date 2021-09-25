# -*- coding: utf-8 -*-

from odoo import models


class ThemeIdeaView(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_ideaview_post_copy(self, mod):
        self.disable_view('website.template_header_default')
        self.enable_view('theme_ideaview.idv_header_template')
    #     self.enable_header_off_canvas()
    #
    #     self.disable_view('website.footer_custom')
    #     self.enable_view('website.template_footer_descriptive')
