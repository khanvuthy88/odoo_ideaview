# -*- coding: utf-8 -*-
import json

import phonenumbers
import werkzeug
import hmac
import odoo
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website.controllers.main import Website
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.float_utils import float_round
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.tools import sql


class WebsiteEventController(WebsiteEventController):
    def _process_tickets_form(self, event, form_details):
        res = super(WebsiteEventController, self)._process_tickets_form(event, form_details)
        return res


class Website(Website):
    _book_per_page = 6

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
    def book_category_author(self, category_id=None, author_id=None, page=1, **kw):
        book_obj = request.env['idv.book'].sudo()
        domain = []
        header_title = 'Books'
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
        pager = request.website.pager(url=url, total=book_count, page=page, step=self._book_per_page, scope=self._book_per_page, url_args=kw)
        book_category = request.env['idv.book.category'].sudo().search([])
        book_author = request.env['res.partner'].sudo().search(
            [('book_author', '=', True), ('book_post_ids', '!=', False)])
        books = book_obj.search(domain, limit=self._book_per_page, offset=pager['offset'])

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

        if book_id.id not in request.session.get('posts_viewed', []):
            if sql.increment_field_skiplock(book_id, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(book_id.id)
                request.session.modified = True

        return request.render('ideaview.idv_single_book', {
            'main_object': book_id,
            'book': book_id,
            'author_obj': author_obj,
            'category_obj': category_obj})

    @http.route('/book/add-to-cart', type='json', auth='public', website=True)
    def add_to_cart(self, **kw):
        book_order = request.session.get('book_order')
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
            return request.env['ir.ui.view']._render_template("ideaview.idv_book_modal_book_detail", {
                'data': kw.get('data'),
            })
        return False

    @http.route('/book/cart/view', type="http", auth="public", website=True)
    def book_view_cart(self):
        return request.render('ideaview.idv_book_cart_view', {})

    @http.route('/book/order/confirmed', type="http", auth="public", methods=['POST'], website=True)
    def book_order_confirmed(self, **post):
        if not post.get('name') or not post.get('phone_number') or not post.get('address'):
            return werkzeug.exceptions.NotFound()
        customer_data = {}
        book_domain = []
        book_data = {}
        data_dict = []
        for key, value in post.items():
            if key == 'name':
                customer_data['name'] = value
            if key == 'phone_number':
                customer_data['phone_number'] = value
            if key == 'address':
                customer_data['address'] = value
            if key.endswith('-id'):
                book = key.split('-')
                if len(book) != 2:
                    continue
                book_data[int(book[0])] = int(value)
                book_domain.append(int(book[0]))

        book_obj = request.env['idv.book'].search([('id', 'in', book_domain)])
        if book_obj:
            # customer = request.env['idv.book.customer'].sudo().create(customer_data)
            book_order_line = []
            for val in book_obj:
                book_order_line.append((0, 0, {
                    'name': val.name,
                    'book_id': val.id,
                    'price_unit': val.price,
                    'qty': book_data.get(val.id),
                }))
            customer = request.env['idv.book.customer'].sudo().create([customer_data])
            request.env['idv.book.order'].sudo().create({
                'customer_id': customer.id,
                "order_line": book_order_line,
            })
            return request.render('ideaview.idv_book_success_booked', {'status': True})
        return request.render('ideaview.idv_book_success_booked', {'status': False})

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
        pager = request.website.pager(url=url, total=post_count, page=page, step=self._book_per_page, scope=self._book_per_page, url_args=kw)
        category_obj = request.env['idv.blog.category'].sudo().search([])
        latest = request.env['idv.blog'].sudo().search([], limit=4)
        posts = post_obj.search(domain, limit=self._book_per_page, offset=pager['offset'])
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

    @http.route('/power-of-reading', type='http', auth='public', website=True)
    def power_of_reading(self):
        faqs = request.env['idv.faq'].sudo().search([])
        power_of_reading = request.env['idv.power.of.reading'].search([])
        return request.render('ideaview.idv_faq_page_template', {
            'faqs': faqs,
            'power_of_reading': power_of_reading,
        })

    @http.route([
        '''/power-of-reading-category/<model('idv.power.of.reading.category'):category_id>''',
        '''/power-of-reading-category/<model('idv.power.of.reading.category'):category_id>/page/<int:page>''',
    ], type="http", auth="public", website=True)
    def power_of_reading_by_category(self, category_id=None, page=0, **kw):
        if not category_id:
            werkzeug.exceptions.NotFound()
        domain = []
        url = '/power-of-reading-category'
        if category_id:
            domain = [('category_id', '=', category_id.id)]
            url = f'/power-of-reading-category/{slug(category_id)}'
        post = request.env['idv.power.of.reading']
        category_obj = request.env['idv.power.of.reading.category'].sudo().search([])
        post_count = post.search_count(domain)
        pager = request.website.pager(url=url, total=post_count, page=page, step=self._book_per_page,
                                      scope=self._book_per_page, url_args=kw)
        latest = request.env['idv.power.of.reading'].sudo().search([], limit=5, order='create_date desc')
        posts = post.search(domain, limit=self._book_per_page, offset=pager['offset'])
        value = {
            'category_obj': category_obj,
            'main_object': category_id,
            'pager': pager,
            'posts': posts,
            'latest': latest,
            'category': category_id,
        }
        return request.render('ideaview.idv_power_of_reading_by_category', value)

    @http.route("/power-of-reading/<model('idv.power.of.reading.category'):category_id>/<model('idv.power.of.reading'):post_id>",
                type='http', auth='public', website=True, sitemap=True)
    def single_power_of_reading(self, category_id=None, post_id=None, **kw):
        if not category_id or post_id:
            werkzeug.exceptions.NotFound()
        category_obj = request.env['idv.power.of.reading.category'].sudo().search([])
        latest = request.env['idv.power.of.reading'].sudo().search([], limit=5, order='create_date desc')
        return request.render('ideaview.idv_power_of_reading_single', {
            'main_object': post_id,
            'power_of_reading': post_id,
            'category_obj': category_obj,
            'latest': latest,
        })

    @http.route([
        '''/product''',
        '''/product/page/<int:page>''',
        '''/product/category/<model('idv.product.category'):category_id>''',
        '''/product/category/<model('idv.product.category'):category_id>/page/<int:page>''',
    ], type="http", auth='public', website=True, sitemap=True)
    def product_index(self, category_id=None, page=0, *kw):
        url = '/product'
        domain = []
        title = 'ផលិតផលទាំងអស់'
        product_category = request.env['idv.product.category'].sudo()
        product_obj = request.env['idv.product'].sudo()
        if category_id:
            url = f'/product/category/{slug(category_id)}'
            domain = [('category_id', '=', category_id.id)]
            title = f'{category_id.name}'
        product_count = product_obj.search_count(domain)
        pager = request.website.pager(url=url, total=product_count, page=page, step=self._book_per_page, scope=self._book_per_page, url_args=kw)
        products = product_obj.search(domain)
        categories = product_category.search([])
        value = {
            'products': products,
            'categories': categories,
            'pager': pager,
            'title': title,
        }
        if category_id:
            value['main_object']: category_id

        return request.render('ideaview.idv_product_index', value)

    @http.route('''/product/<model('idv.product.category'):category_id>/<model('idv.product'):product_id>''',
                type="http", auth='public', website=True, sitemap=True)
    def product_single(self, category_id=None, product_id=None, **kw):
        if not category_id or not product_id:
            return werkzeug.exceptions.NotFound()
        product = request.env['idv.product'].sudo().search([('category_id', '=', category_id.id),
                                                            ('id', '=', product_id.id)], limit=1)
        categories = request.env['idv.product.category'].sudo().search([])
        return request.render('ideaview.idv_product_single', {
            'main_object': product,
            'product': product,
            'categories': categories
        })
