Array.prototype.insert = function (index, item) {
    this.splice(index, 0, item);
};


var ExpensesUI = (function() {
    var __months = [ "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December" ];
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var _$title = null;
    var _$categories = null;
    var _$expenses = null;
    var _curyear = null;
    var _curmonth = null;

    var _maxamount = null;
    var _palette = null;
    var _categories = null;
    var _expenses = null;
    var _latestupdate = null;

    return {
        _initCurrentMonth: function(month, year) {
            _$title.html(month + ' ' + year);
        },

        _init: function() {
            _$categories.empty();
            _$expenses.empty();
            _maxamount = 0.0;
            _palette = Object();
            _categories = Object();
            _expenses = Object();
            _latestupdate = '';

            this._initCurrentMonth(__months[_curmonth], _curyear);
        },

        onReady: function($title, $categories, $expenses) {
            var date = new Date();

            _$title = $title;
            _$categories = $categories;
            _$expenses = $expenses;
            _curyear = date.getYear() + 1900; // Fix relative to 1900
            _curmonth = date.getMonth(); // 0-indexed months

            this._init();
        },


        getYear: function() {
            return _curyear;
        },

        getMonth: function() {
            return _curmonth + 1;
        },

        getLatestUpdate: function() {
            return _latestupdate;
        },

        getMaxAmount: function() {
            return _maxamount;
        },


        onPreviousMonth: function() {
            _curmonth -= 1;
            if (_curmonth < 0) {
                _curmonth = 11;
                _curyear -= 1;
            }

            this._init();
        },

        onNextMonth: function() {
            _curmonth += 1;
            if (_curmonth == 12) {
                _curmonth = 0;
                _curyear += 1;
            }

            this._init();
        },


        _updatePalette: function(obj) {
            /*
             * Add categories to the palette iff the are active (amount != 0.0)
             */
            if (!(obj.name in _palette) && obj.amount != 0.0) {
                _palette[obj.name] = size(_palette);
            }
        },

        _updateMaxAmount: function() {
            _maxamount = 0;
            for (var name in _categories) {
                var curcat = _categories[name];

                if (curcat.amount > _maxamount) {
                    _maxamount = curcat.amount;
                }
            }
        },

        _updateCategory1: function(obj) {
            var prev = _categories[obj.name];

            /*
             * The current category is no more valid (amount equal 0.0).  Check
             * for a previously received update: if present, issue a graceful
             * remove, otherwise return.
             */
            if (obj.amount == 0.0) {
                if (prev === undefined) {
                    return;
                } else {
                    prev.gracefulRemove();
                    delete _categories[prev.name];

                    /*
                     * Find the most expensive category.
                     */
                    this._updateMaxAmount();
                    return;
                }
            }

            /*
             * If we are here, we have received an update for the current
             * category.  First, remove the previous element.
             */
            if (prev !== undefined) {
                prev.remove();
                delete _categories[prev.name];
            }


            /*
             * Then add the new category.
             */
            var newcat = Category(obj.name, obj.amount, obj.currency);
            for (var name in _categories) {
                var curcat = _categories[name];

                if (newcat.name < curcat.name) {
                    newcat.$elem.insertBefore(curcat.$elem);
                    _categories[newcat.name] = newcat;
                    break;
                }
            }
            if (!(newcat.name in _categories)) {
                _$categories.append(newcat.$elem);
                _categories[newcat.name] = newcat;
            }

            /*
             * Update the information about the most expensive category.
             */
            this._updateMaxAmount();

            /*
             * Trigger animations.
             */
            for (var name in _categories) {
                _categories[name].onChanged();
            }
        },

        _updateExpense: function(obj) {
            var prev = _expenses[obj.id];

            /*
             * Update the variable containing the date of the latest update.
             * This operation should be done on all received updates, even those
             * representing deleted items.
             */
            if (obj.updated > _latestupdate) {
                _latestupdate = obj.updated;
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
                    delete _expenses[obj.id];
                    return;
                }
            }

            /*
             * If we are here, we received an update for the current expense.
             * Remove the previous element.
             */
            if (prev !== undefined) {
                prev.remove();
                delete _expenses[prev.id];
            }

            /*
             * Add the expense to internal data structures 
             */
            var newexp = Expense(obj.id, obj.amount, obj.currency,
                    obj.category, obj.note, obj.date);
            for (var id in _expenses) {
                var curexp = _expenses[id];

                if (newexp.date > curexp.date) {
                    newexp.$elem.insertBefore(curexp.$elem);
                    _expenses[newexp.id] = newexp;
                    break;
                }
            }
            if (!(newexp.id in _expenses)) {
                _$expenses.append(newexp.$elem);
                _expenses[newexp.id] = newexp;
            }

            /*
             * Trigger animations.
             */
            newexp.flash();
        },

        onNewData: function(data) {
            $.each(data.categories, EachCallbackWrapper(function(i, value, _this) {
                _this._updatePalette(value);
                _this._updateCategory1(value);
            }, this));

            $.each(data.expenses, EachCallbackWrapper(function(i, value, _this) {
                _this._updateExpense(value);
            }, this));
        },


        getPalette: function(category) {
            return _palette[category];
        },

        formatAmount: function(amount, currency) {
            return sprintf("%.2f %s", amount, currency);
        },

        formatDate: function(date) {
            return date.split(' ')[0]; // XXX format date properly
        }
    };
})();


var Expense = function(ui) {
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
    '<span class="exp_amount">' + ui.formatAmount(amount, currency) + '</span>' +
    '<span class="exp_category palette palette' + ui.getPalette(category) + '">' + category + '</span>' +
    '<span class="exp_note">' + note + '</span>' +
    '<span class="exp_date"><a href="/expenses/' + id + '/edit">' + ui.formatDate(date) + '</a></span>' +
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
}(ExpensesUI);


var Category = function(ui) {
    return function(name, amount, currency) {
        return {
            name: name,
            amount: amount,
            currency: currency,
            $elem: $('' +
'<div class="cat">' +
    '<span class="cat_name">' + name + '</span>' +
    '<span class="cat_amount">' + ui.formatAmount(amount, currency) + '</span>' +
    '<span class="cat_bar_container">' +
        '<span class="cat_bar palette' + ui.getPalette(name) + '"' +
            'style="width: 0%">&nbsp;</span>' +
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
                    };
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


            _onChanged: function() {
                this.$elem.find('.cat_amount').html(
                        ui.formatAmount(this.amount, this.currency));

                var width = 100 * this.amount / ui.getMaxAmount();

                this.$elem.find('.cat_bar').animate({
                    width: width + '%',
                }, ui.__animationtimeout);
            },


            onChanged: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onChanged();
                }, ui.__beforeanimatetimeout, this);
            },
        };
    };
}(ExpensesUI);
