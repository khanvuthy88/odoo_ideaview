# -*- coding: utf-8 -*-
import werkzeug
import hmac
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website.controllers.main import Website


class Website(Website):
    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        book_obj = request.env['idv.book'].sudo()
        new_books = book_obj.search([], limit=4)
        popular_books = book_obj.search([], limit=4)
        search_books = book_obj.search([], limit=4)
        values = {
            'new_books': new_books,
            'popular_books': popular_books,
            'search_books': search_books
        }
        return request.render('ideaview.idv_homepage', values)

    @http.route('/book/<model("idv.book.category"):category_id>/<model("idv.book"):book_id>', type="http",
                auth="public", website=True, sitemap=True)
    def single_book(self, category_id, book_id, **kw):
        if not category_id or not book_id:
            return werkzeug.exceptions.NotFound()
        domain = request.website.website_domain()
        if request.website.is_publisher():
            domain = expression.AND([domain, [('website_published', '=', True)]])
        domain = expression.AND([domain, [('id', '=', book_id.id)]])
        category_obj = request.env['idv.book.category'].sudo().search([])
        book = request.env['idv.book'].sudo().search(domain, limit=1)
        return request.render('ideaview.idv_single_book',
                              {'main_object': book_id, 'book': book_id, 'category_obj': category_obj})

    @http.route('/book/add-to-cart', type='json', auth='public', website=True)
    def add_to_cart(self, **kw):
        if kw.get('bid'):
            print(request.httprequest.environ['HTTP_USER_AGENT'])
            book = request.env['idv.book'].sudo().search([('id', '=', kw.get('bid'))], limit=1)
            print(request.session)
            data = {
                'id': book.id,
                'title': book.name,
                'qty': 1,
                'price': f'{book.price} {book.currency_id.symbol}',
                'total': book.currency_id.round(book.price * 1),
            }
            if request.session.get('idv_add_card'):
                for rec in request.session.get('idv_add_card'):
                    if rec.get('id') == kw.get('bid'):
                        qty = rec.get('qty', 0)
                        rec['qty'] = qty + 1
                    else:
                        request.session.get('idv_add_card').append(data)
            else:
                request.session['idv_add_card'] = [data]
            if book:
                return {'status': True, 'bid': book.id, 'data': data}
        return True
