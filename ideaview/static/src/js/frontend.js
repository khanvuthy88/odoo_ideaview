odoo.define('ideaview.frontend', function (require) {
    'use strict'
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var localStorage = require('web.local_storage');
    var orderIdKey = 'ideaview.add_to_card.order_id';
    var core = require('web.core');
    var QWeb = core.qweb;
    var Dialog = require('web.Dialog');
    var dom = require('web.dom');
    var _t = core._t;
    var data = []
    publicWidget.registry.action_submit_order = publicWidget.Widget.extend({
        selector: 'form#book_registration',
        events: {
            'click button#book-submit-order': "_makeOrderButton",
        },

        _makeOrderButton: function(evt){
            evt.preventDefault();
            console.log(evt);
        },
    });
    publicWidget.registry.idv_frontend = publicWidget.Widget.extend({
        selector: '.idv_website',       
        events:{
            'click .inner-faq ul li h2': '_faqToggle',
            'click a.banner-link': '_makeScroll',
            'click a#add_to_cart': '_addToCart',
        },
        _addToCart: function(evt){
            evt.preventDefault();
            var self = this;
            var orderId = $(evt.currentTarget).data('id');
            return this._rpc({
                route: '/book/add-to-cart',
                params: {
                    'bid': orderId
                },
            }).then(function (data) {
                self.addToCart(data, orderId);
            });
        },
        addToCart: function(data, orderId){
            var self = this;
            let book_obj = []
            let exist = false;
            let cart_item = 0
            if(localStorage.getItem('books')){
                book_obj = JSON.parse(localStorage.getItem('books'));
                _.each(book_obj, function(item){
                    if(item.id == orderId){
                        item.qty +=1
                        item.total += item.price
                        self.exist = true
                    }
                });
                if(self.exist == true){
                    localStorage.removeItem('books');
                    localStorage.setItem('books', JSON.stringify(book_obj));
                    this.do_notify(_t("Success"), _t("Qty has been updated."));
                    return true;
                }
            }
            book_obj.push(data.data);
            cart_item = book_obj.length;
            localStorage.removeItem('books');
            localStorage.setItem('books', JSON.stringify(book_obj));
            this.do_notify(_t("Success"), _t("Cart added."));
            return true;
        },
        _faqToggle: function(evt){
            var target = $(evt.currentTarget).data('target');
            $(evt.currentTarget).toggleClass('expanded');
            $('.'+target).toggleClass('hide');
        },
        _clickScrollAction: function ($el, duration, callback) {
            dom.scrollTo($el[0], {duration: duration}).then(() => callback());
        },
    });
});