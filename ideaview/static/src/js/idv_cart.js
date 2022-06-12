odoo.define('ideaview.idv_cart', function(require) {
    'use strict';
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var localStorage = require('web.local_storage');
    var core = require('web.core');
    var QWeb = core.qweb;
    var dom = require('web.dom');
    var _t = core._t;

    publicWidget.registry.idv_cart = publicWidget.Widget.extend({
        selector: '#idv_book_cart_view',
        xmlDependencies: ['/ideaview/static/src/xml/template.xml'],
        template: 'idv.CartView',
        events: {
            'click span.increase-qty': '_increaseQty',
            'click span.decrease-qty': '_decreaseQty',
            'click button.make-order-js': '_makeOrder',
        },
        init: function(parent, book){
            this._super.apply(this, arguments);
            book = book || {}; 
        },
        willStart: function(){
            return Promise.all([this._super(), this._fetchCartItem()]);
        },
        start: function(){
            var self = this;
            return this._super.apply(arguments).then(function() {
                var book = self._fetchCartItem();
                var total_order = 0.00;
                _.each(book, function(item){
                    total_order += item.total
                });
                self.$el.html(QWeb.render('idv.CartView', {
                    'data': book,
                    'total_order': self.formatNumber(total_order),
                    'disable': book.length > 0 ? false : true
                }));
            });
        },
        /**
         * This function will trigger model and allow customer to input order form
         * @param {*} evt 
         * @returns return Modal
         */
        _makeOrder: function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            var self = this;
            var url = $(evt.currentTarget).data('url');
            var $button = $(evt.currentTarget).closest('[type="submit"]');
            var post = [];
            var book_obj = self._fetchCartItem();
            return ajax.jsonRpc(url, 'call', {'data': book_obj}).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: 'static', keyboard: false});
                $modal.find('.modal-body > div').removeClass('container');
                $modal.appendTo('body').modal();
            });
        },
        /**
         * Decrease order qty
         * @param {*} evt 
         */
        _decreaseQty: function(evt){
            evt.preventDefault();
            var self = this;
            var current_book = $(evt.currentTarget).data('id');
            var book = this._fetchCartItem();
            var total_order = 0.00;
            _.each(book, function(item){
                if(item.id == current_book){
                    item.qty -=1
                    item.total = 0
                    item.total = item.qty * item.price
                }
            });
            var book_obj = _.filter(book, function(item){
                return item.qty > 0;
            });
            _.each(book_obj, function(item){
                total_order += item.total;
            });
            localStorage.removeItem('book');
            localStorage.setItem('books', JSON.stringify(book_obj));
            
            $('#idv_book_cart_view').html(QWeb.render('idv.CartView', {
                'data': book_obj,
                'total_order': self.formatNumber(total_order),
                'disable': book_obj.length > 0 ? false : true
            }));
        },
        /**
         * Increase order qty
         * @param {*} evt 
         */
        _increaseQty: function(evt){
            evt.preventDefault();
            var self = this;
            var current_book = $(evt.currentTarget).data('id');
            var book = this._fetchCartItem();
            var total_order = 0.00;
            if(book.length > 0){
                _.each(book, function(item){
                    if(item.id == current_book){
                        item.qty+=1
                        item.total = 0
                        item.total = item.qty * item.price
                    }
                });
                localStorage.removeItem('books');
                localStorage.setItem('books', JSON.stringify(book));                
                this.do_notify(_t("Success"), _t("Qty has been updated."));
                _.each(this._fetchCartItem(), function(item){
                    total_order += item.total;
                });
                $('#idv_book_cart_view').html(QWeb.render('idv.CartView', {
                    'data': book,
                    'total_order': self.formatNumber(total_order),
                    'disable': book.length > 0 ? false : true
                }));
            }
        },
        formatNumber: function(value=0.00){
            return value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        _fetchCartItem: function(){
            var book = JSON.parse(localStorage.getItem('books'));
            return book ? book : {};
        }
    });
});