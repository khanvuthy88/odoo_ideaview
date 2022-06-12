# -*- coding: utf-8 -*-
{
    'name': "IDear View",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['theme_ideaview'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/snippets/s_about_us.xml',
        'views/snippets/snippets.xml',
        'views/website_snippets.xml',
        'data/website_data.xml',
        'data/data.xml',
        'views/views.xml',
        'views/res_partner.xml',
        'views/book_category_view.xml',
        'views/book_view.xml',
        'views/blog_category_view.xml',
        'views/blog_post_view.xml',
        'views/book_customer_view.xml',
        'views/book_order_view.xml',
        'views/faq_view.xml',
        'views/product_category_view.xml',
        'views/product_view.xml',
        'views/idv_power_of_reading_views.xml',
        'views/menu_view.xml',
        'views/assets.xml',
        'views/templates.xml',
        'views/idv_power_of_reading_by_category.xml',
        'views/product_templates.xml',
    ],
    'license': 'LGPL-3',
    'qweb': [
        'static/src/xml/template.xml',
    ]
}
