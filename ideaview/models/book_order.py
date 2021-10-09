# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.http import request


class BookAuthor(models.Model):
    _name = 'idv.book.customer'
    _description = "Idea view book customer"

    name = fields.Char(required=True)
    phone_number = fields.Char(required=True)
    address = fields.Char()


class BookOrder(models.Model):
    _name = 'idv.book.order'
    _description = 'Idea View book order'

    name = fields.Char()
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    customer_id = fields.Many2one('idv.book.customer', required=True)
    phone_number = fields.Char(related='customer_id.phone_number')
    address = fields.Char(related='customer_id.address')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True)
    order_line = fields.One2many('idv.book.order.line', 'order_id', string='Order Lines',
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    @api.model
    def create(self, value):
        value['name'] = self.env['ir.sequence'].next_by_code('idv.sale.order') or _('New')
        result = super(BookOrder, self).create(value)
        return result


class BookOrderLine(models.Model):
    _name = 'idv.book.order.line'
    _description = "Book Order Line"

    @api.depends('price_unit', 'qty')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.qty * line.price_unit

    order_id = fields.Many2one('idv.book.order', string='Order Reference', required=True, ondelete='cascade',
                               index=True,
                               copy=False)
    book_id = fields.Many2one('idv.book')
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    qty = fields.Integer()

    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True, index=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Book Price', default=0.0)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    price_subtotal = fields.Monetary(compute="_compute_amount", store=True)

    @api.onchange('book_id')
    def book_id_change(self):
        self.qty = 1
        self.price_unit = self.book_id.price
        self.name = self.book_id.name
