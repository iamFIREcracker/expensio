Array.prototype.insert = function (index, item) {
    this.splice(index, 0, item);
};


function size(obj) {
    var size = 0, key;

    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }

    return size;
}


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
        onReady: function($title, $categories, $expenses) {
            var date = new Date();

            _$title = $title;
            _$categories = $categories;
            _$expenses = $expenses;
            _curyear = date.getYear() + 1900; // Fix relative to 1900
            _curmonth = date.getMonth(); // 0-indexed months

            this._init();
        },

        _init: function() {
            _$categories.empty();
            _$expenses.empty();
            _maxamount = 0.0;
            _palette = Object();
            _categories = Object();
            _expenses = Array();
            _latestupdate = '1970-01-01 00:00:00.000000'; // epoch

            this.renderCurrentMonth(__months[_curmonth], _curyear);
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

        _updateCategory: function(cat) {
            var currency = cat.currency;

            if (!(cat.name in _palette)) {
                _palette[cat.name] = size(_palette);
                _categories[cat.name] = Category(cat.name, 0, currency);
                _$categories.append(_categories[cat.name].$elem);
            }
            _categories[cat.name].setAmount(cat.amount);

            if (cat.amount > _maxamount) {
                _maxamount = cat.amount;
            }

            // Notify all the categories that a new normalization factor has
            // been set.
            for (catname in _categories) {
                _categories[catname].onDisplay();
            }
        },

        _updateExpense: function(exp) {
            var e = Expense(exp.id, exp.amount, exp.currency,
                    exp.category, exp.note, exp.date);
            var put = false;

            if (_expenses.length != 0) {
                for (var i = 0; i < _expenses.length; i++) {
                    var curexpense = _expenses[i];

                    if (e.date > curexpense.date) {
                        e.$elem.insertBefore(curexpense.$elem);
                        _expenses.insert(i, e);
                        put = true;
                        break;
                    }
                }
            }
            if (!put) {
                _$expenses.append(e.$elem);
                _expenses.push(e);
            }

            if (exp.updated > _latestupdate) {
                _latestupdate = exp.updated;
            }

            e.onDisplay();
        },

        onNewData: function(data) {
            $.each(data.categories, function(this_) {
                return function() {
                    this_._updateCategory(this);
                }
            }(this));

            $.each(data.expenses, function(this_) {
                return function() {
                    this_._updateExpense(this);
                };
            }(this));
        },

        renderCurrentMonth: function(month, year) {
            _$title.html(month + ' ' + year);
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
    return function(id, amount, currency, catname, note, date) {
        return {
            amount: amount,
            currency: currency,
            catname: catname,
            note: note,
            date: date,
            $elem: $('' +
'<div class="exp">' +
    '<span class="exp_amount">' + ui.formatAmount(amount, currency) + '</span>' +
    '<span class="exp_category palette palette' + ui.getPalette(catname) + '">' + catname + '</span>' +
    '<span class="exp_note">' + note + '</span>' +
    '<span class="exp_date"><a href="/expenses/' + id + '/edit">' + ui.formatDate(date) + '</a></span>' +
'</div>'
                ),
            _timeoutid: null,

            onDisplay: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(this_) {
                    return function() {
                        var oldbackground = this_.$elem.css('backgroundColor');

                        this_.$elem.css('backgroundColor', '#ffff9c');
                        this_.$elem.delay(ui.__animationtimeout).animate({
                            backgroundColor: oldbackground
                        }, 'slow');
                    };
                }(this), ui.__beforeanimatetimeout);
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
            _$elem_amount: null,
            _$elem_bar: null,
            _timeoutid: null,

            setAmount: function(amount_) {
                this.amount = amount_;

                this._onSetAmount();
            },

            _onSetAmount: function() {
                // Cache the value
                if (this._$elem_amount == null) {
                    this._$elem_amount = this.$elem.find('.cat_amount');
                }

                this._$elem_amount.html(ui.formatAmount(this.amount, this.currency));
            },

            onDisplay: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(this_) {
                    return function() {
                        // Cache the value
                        if (this_._$elem_bar == null) {
                            this_._$elem_bar = this_.$elem.find('.cat_bar');
                        }

                        var width = 100 * this_.amount / ui.getMaxAmount();
                        this_._$elem_bar.animate({
                            width: width + '%',
                        }, ui.__animationtimeout);
                    };
                }(this), ui.__beforeanimatetimeout);
            }
        };
    };
}(ExpensesUI);
