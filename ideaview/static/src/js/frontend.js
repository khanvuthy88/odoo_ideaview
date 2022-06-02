odoo.define('ideaview.frontend', function (require) {
    'use strict'
    var ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');
    var localStorage = require('web.local_storage');
    var orderIdKey = 'ideaview.add_to_card.order_id';
    var core = require('web.core');
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
            'click a#add_to_cart': '_addToCart',
            'click span.decrease-qty': "_decreaseQty",
            'click span.increase-qty': "_increaseQty",
            'click button.make-order-js': "_makeOrderJs",
            'click .inner-faq ul li h2': '_faqToggle',
            'click a.banner-link': '_makeScroll'
        },
        start: function () {
            var self = this;
            return this._super.apply(arguments).then(function() {
                self._renderTable();
            });
        },
        _makeScroll: function(evt){
            evt.preventDefault();
            console.log(evt);
            var $el = $(evt.currentTarget.hash);
            var url = $(evt.currentTarget).data('url');
            this._clickScrollAction($el, 500, function(){});
        },
        _makeOrderButton: function(evt){      
            evt.preventDefault();
            console.log(evt);
            // evt.stopPropagation();
            var book_obj = JSON.parse(localStorage.getItem('books'));
            return;
        },
        _removeArray: function(array, key, value){
            console.log(key);
            return array.filter((obj) => {
                return obj[key] != value;
            });
        },
        _renderTable: function(){
            if(localStorage.getItem('books')){
                let book = JSON.parse(localStorage.getItem('books'));
                if($('tbody.table-cart-item')){
                    var t = "";
                    $.each(book, function(i, v) {
                       t += '<tr><td>'+v.title+'</td><td><span data-id="'+v.id+'" class="btn btn-link rounded decrease-qty"><i data-id="'+v.id+'" class="fa fa-minus-circle"/></span>'+v.qty+'<span data-id="'+v.id+'" class="btn btn-link rounded increase-qty"><i data-id="'+v.id+'" class="fa fa-plus-circle"/></span></td><td>'+ new Intl.NumberFormat().format(v.price)+' ៛</td><td style="width:150px"><img class="rounded img" style="width:30px; height:auto;" src="'+v.image+'"/></td></tr>';
                    });
                    $('tbody.table-cart-item').empty();
                    $('tbody.table-cart-item').append(t);
                }
                let total = book.reduce((n, {total}) => n + total, 0);
                $('span.book-ordered-total').text(new Intl.NumberFormat().format(total));
            }
        },
        _decreaseQty: function(evt){
            let id = parseInt($(evt.currentTarget).data('id'));
            let book_obj = JSON.parse(localStorage.getItem('books'));
            let remove = false;
            for(var i =0; i < book_obj.length; i++){
                if(book_obj[i].id == id){
                    if(book_obj[i].qty == 1){
                        remove = true;
                    }else{
                        book_obj[i].qty -=1;
                        book_obj[i].total = book_obj[i].price * book_obj[i].qty;
                    }
                }
            }
            if(remove == true){
                book_obj = this._removeArray(book_obj, 'id', id);
            }
            localStorage.removeItem('books');
            localStorage.setItem('books', JSON.stringify(book_obj));
            this.do_notify(_t("Success"), _t("Qty has been updated."));
            this._renderTable();
        },
        _increaseQty: function(evt){
            let id = parseInt($(evt.currentTarget).data('id'));
            let book_obj = JSON.parse(localStorage.getItem('books'));
            for(var i =0; i < book_obj.length; i++){
                if(book_obj[i].id == id){
                    book_obj[i].qty +=1;
                    book_obj[i].total = book_obj[i].price * book_obj[i].qty;
                }
            }
            localStorage.removeItem('books');
            localStorage.setItem('books', JSON.stringify(book_obj));
            this.do_notify(_t("Success"), _t("Qty has been updated."));
            this._renderTable();
        },
        addToCart: function(data, orderId){
            let book_obj = []
            let exist = false;
            let cart_item = 0
            if(localStorage.getItem('books')){
                book_obj = JSON.parse(localStorage.getItem('books'));
                for(var i = 0; i<book_obj.length; i++){
                    if(book_obj[i].id == orderId){
                        book_obj[i].qty +=1;
                        book_obj[i].total = book_obj[i].price * book_obj[i].qty;
                        this.exist = true;
                    }
                }
                if(this.exist == true){
                    cart_item = book_obj.length;
                    localStorage.removeItem('books');
                    localStorage.setItem('books', JSON.stringify(book_obj));
                    this.do_notify(_t("Success"), _t("Qty has been updated."));
                    return true;
                }
            }
            book_obj.push(data.data);
            cart_item = book_obj.length;
            localStorage.setItem('books', JSON.stringify(book_obj));
            this.do_notify(_t("Success"), _t("Cart added."));
            $('span.cart-item').text(cart_item);
            return true;
        },
        validatePhoneNumber: function(input_str){
            var re = /^\(?(\d{3})\)?[- ]?(\d{3})[- ]?(\d{4})$/;
            return re.test(input_str);
        }, 

        _makeOrderJs: function(evt){
            evt.preventDefault();
            evt.stopPropagation();
            var url = $(evt.currentTarget).data('url');
            var $button = $(evt.currentTarget).closest('[type="submit"]');
            var post = [];
            var book_obj = JSON.parse(localStorage.getItem('books'));
            return ajax.jsonRpc(url, 'call', {'data': book_obj}).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: 'static', keyboard: false});
                $modal.find('.modal-body > div').removeClass('container');
                $modal.appendTo('body').modal();
            });
        },
        _addToCart: function(evt){
            evt.preventDefault();
            var self = this;
            var orderId = $('a#add_to_cart').data('id');
            return this._rpc({
                route: '/book/add-to-cart',
                params: {
                    'bid': orderId
                },
            }).then(function (data) {
                self.addToCart(data, orderId);
            });
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