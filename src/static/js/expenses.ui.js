var ExpensesUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var palette = null;
    var $expenses = null;

    var expenses = null;
    var latest = null;


    var init = function() {
        $expenses.empty();
        expenses = Object();
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
                return;
            } else {
                prev.gracefulRemove();
                delete expenses[obj.id];
                return;
            }
        }

        /*
         * If we are here, we received an update for the current expense.
         * Remove the previous element.
         */
        if (prev !== undefined) {
            prev.remove();
            delete expenses[prev.id];
        }

        /*
         * Add the expense to internal data structures 
         * XXX fix ordering!!!!
         */
        var newexp = Expense(obj.id, obj.amount, obj.currency,
                obj.category, obj.note, obj.date);
        for (var id in expenses) {
            var curexp = expenses[id];

            if (newexp.date > curexp.date) {
                newexp.$elem.insertBefore(curexp.$elem);
                expenses[newexp.id] = newexp;
                break;
            }
        }
        if (!(newexp.id in expenses)) {
            $expenses.append(newexp.$elem);
            expenses[newexp.id] = newexp;
        }

        /*
         * Trigger animations.
         */
        newexp.flash();
    };

    return {
        onReady: function(palette_, $expenses_) {
            palette = palette_;
            $expenses = $expenses_;

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            $.each(data.expenses, EachCallbackWrapper(function(i, value, _this) {
                updateExpense(value);
            }, this));
        },


        getLatest: function() {
            return latest;
        },
    };
})();


var Expense = function(ui, palette, formatter) {
    return function(id, amount, currency, category, note, date) {
        return {
            id: id,
            amount: amount,
            currency: currency,
            category: category,
            note: note,
            date: date,
            $elem: $('' +
'<div class="exp">' +
    '<span class="exp_amount">' + formatter.amount(amount, currency) + '</span>' +
    '<span class="exp_inner">' +
        '<span class="exp_category palette" ' +
            'style="background-color: '+ palette.background(category) + '; ' +
                'color: ' + palette.foreground(category) + '">' +
                category +
        '</span>' +
        '<span class="exp_note">' + note + '</span>' +
    '</span>' +
    '<span class="exp_date"><a href="/expenses/' + id + '/edit">' + formatter.date(date) + '</a></span>' +
'</div>'
                ),
            _timeoutid: null,


            remove: function() {
                this.$elem.remove();
            },

            _onGracefulRemove: function() {
                this.$elem.addClass('removed')
                    .fadeOut('slow', function(_this) {
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
