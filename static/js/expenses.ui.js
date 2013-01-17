var ExpensesUI = (function() {
    var __help = 'This section bla bla bla...';
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var formatter = null;
    var palette = null;
    var $title = null;
    var $expenses = null;
    var expenses = null;
    var latest = null;
    var addexpenselisteners = Array();
    var first = null;


    var init = function() {
        $title.html("&nbsp");
        $expenses.html('<div class="loading"><img src="/static/images/loading.gif" /></div>')
        expenses = Object();
        latest = '';
        first = true;
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
            } else {
                prev.gracefulRemove();
                delete expenses[obj.id];
                return true;
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
            $expenses.append(newexp.$elem);
            expenses[newexp.id] = newexp;
        }

        /*
         * Trigger animations and notify listeners
         */
        newexp.flash();
        $.each(addexpenselisteners, function(index, func) {
            func(newexp);
        })

        return true;
    };

    var updateTitle = function() {
        var overall = 0.0;
        var currency = '';

        $.each(expenses, function() {
            overall += this.amount;
            currency = this.currency;
        });

        $title.text(sprintf("Total: %s", formatter.amount(overall, currency)));
    };

    var showHelp = function() {
        $expenses.html('<div class="help"><p>' + __help + '</p></div>');
    }

    return {
        onReady: function(formatter_, palette_, $title_, $expenses_) {
            formatter = formatter_;
            palette = palette_;
            $title = $title_;
            $expenses = $expenses_;

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            var hidehelp = false;

            if ($expenses.find('.loading').length) {
                $expenses.empty();
            }

            $.each(data.expenses, EachCallbackWrapper(function(i, value, _this) {
                hidehelp = hidehelp || updateExpense(value);
            }, this));
            updateTitle();

            if (!hidehelp && first) {
                showHelp();
            }
            first = false;
        },

        confirmDelete: function(exp) {
            var msg = sprintf(
                    'You are about to delete an expense (Amount: %s, Category: %s, Date: %s)',
                    formatter.amount(exp.amount, exp.currency),
                    exp.category, formatter.date(exp.date));
            return window.confirm(msg);
        },

        addExpense: function(func) {
            addexpenselisteners.push(func)
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
        '<img src="/static/images/attachment.png" alt="Attachment icon" />' +
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
    addAttachment(attachment, note) +
    '<span class="exp_amount">' + formatter.amount(amount, currency) + '</span>' +
    '<span class="exp_inner">' +
        '<span class="exp_category palette" ' +
            'style="background-color: '+ palette.background(category) + '; ' +
                'color: ' + palette.foreground(category) + '">' +
                category +
        '</span>' +
        '<span class="exp_note">' + note + '</span>' +
    '</span>' +
    '<span class="exp_date">' + formatter.date(date) + '</span>' +
    '<span class="exp_edit">' +
        '<a href="/expenses/' + id + '/edit" title="Edit expense">' +
            '<img src="/static/images/edit.png" alt="Edit expense icon"/>' +
        '</a>' +
    '</span>' +
    '<form class="exp_delete" method="post">' +
        '<input type="hidden" value="' + id + '" name="id" id="id"/>' +
        '<a href="/expenses/' + id + '/delete" title="Delete expense">' +
            '<img src="/static/images/delete.png" alt="Delete expense icon"/>' +
        '</a>' +
    '</form>' +
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
