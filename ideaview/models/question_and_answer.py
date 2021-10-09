# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.http import request


class FAQ(models.Model):
    _name = "idv.faq"
    _description = "FAQ"
    
    name = fields.Char()
    question = fields.Char()
    answer = fields.Text()
    
    @api.model
    def create(self, value):
        value['name'] = value['question']
        return super(FAQ, self).create(value)
