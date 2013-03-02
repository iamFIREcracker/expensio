var ExpensesUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var formatter = null;
    var palette = null;
    var $help = null;
    var $expenses = null;
    var $inner = null;
    var expenses = null;
    var latest = null;
    var addexpenselisteners = [];
    var remexpenselisteners = [];


    var init = function() {
        $inner.empty();
        $expenses.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        expenses = {};
        latest = '';
    };

    var updateExpense = function(obj) {
        var prev = expenses[obj.id];

        /*
         * Update the variable containing the date of the latest update.
         * This operation should be done on all received updates, even those
         * representing deleted items.
         */
        if (obj.updated > latest) {
            latest = obj.updated;
        }

        /*
         * The current expense has been deleted.  Check for a previously
         * received update: if preset, issue a graceful remove, otherwise
         * skip the element and return.
         */
        if (obj.deleted === true) {
            if (prev === undefined) {
                return false;
            }
            prev.gracefulRemove();
            delete expenses[obj.id];

            $.each(remexpenselisteners, function(index, func) {
                func(prev);
            });

            return true;
        }

        /*
         * If we are here, we received an update for the current expense.
         * Remove the previous element.
         */
        if (prev !== undefined) {
            prev.remove();
            delete expenses[prev.id];

            $.each(remexpenselisteners, function(index, func) {
                func(prev);
            });
        }

        if ($expenses.find('.help').length) {
            $inner.empty();
        }

        /*
         * Add the expense to internal data structures 
         * XXX fix ordering!!!!
         */
        var newexp = Expense(obj.id, obj.amount, obj.currency,
                obj.category, obj.note, obj.date, obj.attachment);

        for (var id in expenses) {
            var curexp = expenses[id];

            if (newexp.date > curexp.date) {
                newexp.$elem.insertBefore(curexp.$elem);
                expenses[newexp.id] = newexp;
                break;
            }
        }
        if (!(newexp.id in expenses)) {
            $inner.append(newexp.$elem);
            expenses[newexp.id] = newexp;
        }

        /*
         * Trigger animations and notify listeners
         */
        newexp.flash();
        $.each(addexpenselisteners, function(index, func) {
            func(newexp);
        });

        return true;
    };

    return {
        onReady: function(formatter_, palette_, $expenses_) {
            formatter = formatter_;
            palette = palette_;
            $expenses = $expenses_;
            $inner = $expenses.find('#expenses-inner');
            $help = $expenses.find('.alert');

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            var $loading = $expenses.find('.loading');

            if ($loading.length) {
                $loading.remove();
            }

            _.map(data.expenses, updateExpense);

            if (_.any(expenses) == false) {
                $inner.hide();
                $help.show();
            } else {
                $help.hide();
                $inner.show();
            }
        },

        expensesAdd: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Add expense</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        expensesEdit: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Edit expense</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        expensesDelete: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Delete expense</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        addExpense: function(func) {
            addexpenselisteners.push(func)
        },

        remExpense: function(func) {
            remexpenselisteners.push(func)
        },

        getLatest: function() {
            return latest;
        },
    };
})();


var Expense = function(ui, palette, formatter) {
    return function(id, amount, currency, category, note, date, attachment) {
        var addAttachment = function(attachment, note) {
            if (attachment == null)
                return '' +
'<span class="exp_attach">' +
'</span>';
            else
                return '' +
'<span class="exp_attach">' +
    '<a href="' + attachment + '" rel="lightbox" title="' + note + '">' +
        '<i class="icon-file"></i>' +
    '</a>' +
'</span>';
        };

        return {
            id: id,
            amount: amount,
            currency: currency,
            category: category,
            note: note,
            date: date,
            attachment: attachment,
            $elem: $('' +
'<div class="exp">' +
    '<span class="exp_date">' + formatter.date(date) + '</span>' +
    '<span class="exp_inner">' +
        '<span class="exp_category palette" ' +
            'style="background-color: '+ palette.background(category) + '; ' +
                'color: ' + palette.foreground(category) + '">' +
                category +
        '</span>' +
        '<span class="exp_note">' + note + '</span>' +
    '</span>' +
    '<span class="exp_amount">' + formatter.amount(amount, currency) + '</span>' +
    addAttachment(attachment, note) +
    '<span class="exp_edit">' +
        '<a href="/expenses/' + id + '/edit" title="Edit expense">' +
            '<i class="icon-pencil"></i>' +
        '</a>' +
    '</span>' +
    '<span class="exp_delete">' +
        '<a href="/expenses/' + id + '/delete" title="Delete expense">' +
            '<i class="icon-remove"></i>' +
        '</a>' +
    '</span>' +
'</div>'
                ),
            _timeoutid: null,


            remove: function() {
                this.$elem.remove();
            },

            _onGracefulRemove: function() {
                this.$elem.fadeOut('slow', function(_this) {
                    return function() {
                        _this.remove();
                    }
                }(this));
            },

            gracefulRemove: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onGracefulRemove();
                }, ui.__beforeanimatetimeout, this);
            },


            _onFlash: function() {
                this.$elem.addClass('flash')
                    .delay(ui.__animationtimeout).removeClass('flash', 'slow');
            },

            flash: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onFlash();
                }, ui.__beforeanimatetimeout, this);
            },
        };
    };
}(ExpensesUI, PaletteManager, Formatter);
