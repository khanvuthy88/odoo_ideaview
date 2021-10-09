# -*- coding: utf-8 -*-
import werkzeug
import hmac
import odoo
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website.controllers.main import Website
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.float_utils import float_round


class Website(Website):
    @http.route('/', type='http', auth="public", website=True, sitemap=True)
    def index(self, **kw):
        book_obj = request.env['idv.book'].sudo()
        new_books = book_obj.search([], limit=4)
        popular_books = book_obj.search([], limit=4)
        search_books = book_obj.search([], limit=4)
        latest_blog = request.env['idv.blog'].sudo().search([], limit=6)
        values = {
            'new_books': new_books,
            'popular_books': popular_books,
            'search_books': search_books,
            'latest_blog': latest_blog
        }
        return request.render('ideaview.idv_homepage', values)

    @http.route([
        '''/book''',
        '''/book/page/<int:page>''',
        '''/book/<model("idv.book.category"):category_id>''',
        '''/book/<model("idv.book.category"):category_id>/page/<int:page>''',
        '''/book/author/<model("res.partner"):author_id>''',
        '''/book/author/<model("res.partner"):author_id>/page/<int:page>''',
    ], type="http", auth="public", website=True, sitemap=True)
    def book_category_author(self, category_id=None, author_id=None, page=0, **kw):
        book_obj = request.env['idv.book'].sudo()
        domain = []
        header_title = ''
        url = '/book'
        if category_id:
            domain = [('book_category', '=', category_id.id)]
            url = f'/book/{slug(category_id)}'
            header_title = f'{category_id.name}'
        if author_id:
            if not author_id.book_author:
                return werkzeug.exceptions.NotFound()
            domain = [('author_id', '=', author_id.id)]
            url = f'/book/author/{slug(author_id)}'
            header_title = f'{author_id.name}'
        book_count = book_obj.search_count(domain)
        pager = request.website.pager(url=url, total=book_count, page=page, step=3, scope=3, url_args=kw)
        book_category = request.env['idv.book.category'].sudo().search([])
        book_author = request.env['res.partner'].sudo().search(
            [('book_author', '=', True), ('book_post_ids', '!=', False)])
        books = book_obj.search(domain)

        value = {
            'header_title': header_title,
            'pager': pager,
            'book_category': book_category,
            'book_author': book_author,
            'books': books,
        }
        if category_id:
            value['main_object'] = category_id
        if author_id:
            value['main_object'] = author_id
        return request.render('ideaview.idv_book_author_category', value)

    @http.route('/book/<model("idv.book.category"):category_id>/<model("idv.book"):book_id>', type="http",
                auth="public", website=True, sitemap=True)
    def single_book(self, category_id, book_id, **kw):
        if not category_id or not book_id:
            return werkzeug.exceptions.NotFound()
        domain = request.website.website_domain()
        if request.website.is_publisher():
            domain = expression.AND([domain, [('website_published', '=', True)]])
        category_obj = request.env['idv.book.category'].sudo().search([])
        author_obj = request.env['res.partner'].sudo().search(
            [('book_author', '=', True), ('book_post_ids', '!=', False)])

        return request.render('ideaview.idv_single_book', {
            'main_object': book_id,
            'book': book_id,
            'author_obj': author_obj,
            'category_obj': category_obj})

    @http.route('/book/add-to-cart', type='json', auth='public', website=True)
    def add_to_cart(self, **kw):
        book_order = request.session.get('book_order')
        print(book_order)
        value = {
            'status': False,
            'data': []
        }
        if not kw.get('bid'):
            value['status'] = False
        book = request.env['idv.book'].sudo().search([('id', '=', kw.get('bid'))], limit=1)
        if book:
            data = {
                'id': book.id,
                'title': book.name,
                'price': float_round(book.price, 2),
                'total': 0,
                'qty': 1,
                'image': f"{request.env['website'].image_url(book, 'image_1024')}"
            }
            if not book_order:
                request.session['book_order'] = [book.id]
            else:
                book_order.append(book.id)
                request.session['book_order'] = book_order
            value = {
                'status': True,
                'data': data,
            }
        return value

    @http.route('/book/book-order/confirm', type='json', auth='public', website=True)
    def book_order_confirm(self, **kw):
        if kw.get('data'):
            print(kw.get('data'))
            return {'status': True}
        return False

    @http.route('/book/cart/view', type="http", auth="public", website=True)
    def book_view_cart(self):
        return request.render('ideaview.idv_book_cart_view', {})

    @http.route('/book/order/confirmed', type="json", auth="public", website=True, csrf=False)
    def book_order_confirmed(self, **kw):
        if not kw.get('data'):
            return werkzeug.exceptions.NotFound()
        order_lines = []
        user_data = [{'name': rec.get('name'), 'phone_number': rec.get('phone_number'), 'address': rec.get('address')}
                     for rec in kw.get('user_data')]
        for line in kw.get('data'):
            book = request.env['idv.book'].search([('id', '=', line.get('id'))], limit=1)
            if book:
                order_lines.append((0, 0, {
                    'name': book.name,
                    'book_id': book.id,
                    'price_unit': book.price,
                    'qty': line.get('qty'),
                }))
        customer = request.env['idv.book.customer'].sudo().create(user_data)

        request.env['idv.book.order'].sudo().create({
            'customer_id': customer.id,
            "order_line": order_lines,
        })
        return {'status': True}

    @http.route([
        '''/blog/''',
        '''/blog/page/<int:page>''',
        '''/blog/<model('idv.blog.category'):category_id>''',
        '''/blog/<model('idv.blog.category'):category_id>/page/<int:page>''',
        '''/blog/author/<model('res.partner'):author_id>''',
        '''/blog/author/<model('res.partner'):author_id>/page/<int:page>''',
    ], type="http", auth="public", website=True, sitemap=True)
    def post_by_category(self, category_id=None, author_id=None, page=0, **kw):
        post_obj = request.env['idv.blog'].sudo()
        domain = []
        category = 'អត្ថបទចែករំលែក'
        url = '/blog'
        if category_id:
            domain = [('category_id', '=', category_id.id)]
            url = f'/blog/{slug(category_id)}'
            category = f'{category_id.name}'
        if author_id:
            domain = [('author_id', '=', author_id.id)]
            url = f'/blog/author/{slug(author_id)}'
            category = f'{author_id.name}'
        post_count = post_obj.search_count(domain)
        pager = request.website.pager(url=url, total=post_count, page=page, step=3, scope=3, url_args=kw)
        category_obj = request.env['idv.blog.category'].sudo().search([])
        latest = request.env['idv.blog'].sudo().search([], limit=4)
        posts = post_obj.search(domain, limit=3, offset=pager['offset'])
        value = {
            'pager': pager,
            'category_obj': category_obj,
            'latest': latest,
            'posts': posts,
            'category': category,
        }
        if category_id:
            value['main_object'] = category_id
        if author_id:
            value['main_object'] = author_id
        return request.render('ideaview.idv_blog_post_by_category', value)

    @http.route('/blog/<model("idv.blog.category"):category_id>/<model("idv.blog"):blog_id>',
                type="http", auth="public", website=True, sitemap=True)
    def single_post(self, category_id, blog_id):
        if not category_id or not blog_id:
            return werkzeug.exceptions.NotFound()
        category_obj = request.env['idv.blog.category'].sudo().search([])
        author_obj = request.env['res.partner'].sudo().search([('book_author', '=', True)])
        latest = request.env['idv.blog'].sudo().search([], limit=4)
        value = {
            "main_object": blog_id,
            'blog': blog_id,
            'category_obj': category_obj,
            'author_obj': author_obj,
            'latest': latest,
        }
        return request.render('ideaview.idv_blog_post_single', value)

    @http.route('/power-of-reading-1', type='http', auth='public', website=True)
    def power_of_reading(self):
        faqs = request.env['idv.faq'].sudo().search([])
        return request.render('ideaview.idv_faq_page_template', {'faqs': faqs})
