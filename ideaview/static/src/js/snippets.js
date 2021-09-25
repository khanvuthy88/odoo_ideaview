odoo.define('ideaview.dynamic_snippet', function (require) {
    'use strict'
    var publicWidget = require('web.public.widget');
    publicWidget.registry.books = publicWidget.Widget.extend({
        selector: '.book_snippet',
        disabledInEditableMode: false,
        start: function () {
            var self = this;
            var rows = this.$el[0].dataset.numberOfBooks || '5';
            this.$el.find('td').parents('tr').remove();
            this._rpc({
                model: 'idv.book',
                method: 'search_read',
                domain: [],
                fields: ['name', 'price'],
                orderBy: [{ name: 'name', asc: false }],
                limit: parseInt(rows)
            }).then(function(res){
                _.each(res, function (book) {
                    self.$el.append(
                        $('<tr />').append(
                            $('<td />').text(book.name),
                            $('<td />').text(book.price)
                        )
                    );
                });
            });
        },
    });
});