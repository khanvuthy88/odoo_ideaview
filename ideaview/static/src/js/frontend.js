odoo.define('ideaview.frontend', function (require) {
    'use strict'
    var publicWidget = require('web.public.widget');
    var localStorage = require('web.local_storage');
    var orderIdKey = 'ideaview.add_to_card.order_id';
    var core = require('web.core');
    var _t = core._t;
    var data = []
    publicWidget.registry.idv_frontend = publicWidget.Widget.extend({
        selector: '.idv_website',
        events:{
            'click a#add_to_cart': '_addToCart'
        },
        start: function () {
            return this._super.apply(this, arguments);
        },
        addProduct: function(data){
            let product = []
            if(localStorage.getItem('products')){
                products = JSON.parse(localStorage.getItem('products'));
            }
            products.push({'productId' : productId + 1, image : '<imageLink>'});
            localStorage.setItem('products', JSON.stringify(products));
        },
        _addToCart: function(evt){
            var orderId = $('a#add_to_cart').data('id');
            var bname = $('div.inner-summary > h1')
            var image = $('#idv_single_book > div > div > div.col-md-9 > div > div > article > div > div.summary > div.post-thumbnail > span > img')
        },
    });
});