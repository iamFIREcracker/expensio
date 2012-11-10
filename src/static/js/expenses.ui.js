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
    return {
        __months: [ "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December" ],
        __animationtimeout: 200, // milliseconds
        _$categories: null,
        _$expenses: null,
        _maxamount: null,
        _palette: null,
        _categories: null,
        _expenses: null,
        _curmonth: null,
        _curyear: null,
        _latestupdate: null,

        onReady: function($title, $categories, $expenses) {
            var date = new Date();

            this._$title = $title;
            this._$categories = $categories;
            this._$expenses = $expenses;
            this._curyear = date.getYear() + 1900; // Fix relative to 1900
            this._curmonth = date.getMonth(); // 0-indexed months

            this._init();
        },

        _init: function() {
            this._$categories.empty();
            this._$expenses.empty();
            this._maxamount = 0.0;
            this._palette = {};
            this._categories = {};
            this._expenses = Array();
            this._latestupdate = '1970-01-01 00:00:00.000000'; // epoch

            this.renderCurrentMonth(this.__months[this._curmonth], this._curyear);
        },

        onPreviousMonth: function() {
            this._curmonth -= 1;
            if (this._curmonth < 0) {
                this._curmonth = 11;
                this._curyear -= 1;
            }

            this._init();
        },


        onNextMonth: function() {
            this._curmonth += 1;
            console.log(this._curmonth);
            if (this._curmonth == 12) {
                this._curmonth = 0;
                this._curyear += 1;
            }

            this._init();
        },

        getYear: function() {
            return this._curyear;
        },

        getMonth: function() {
            return this._curmonth + 1;
        },

        getLatestUpdate: function() {
            return this._latestupdate;
        },

        _updateCategory: function(exp) {
            var catname = exp.category;
            var currency = exp.currency;

            if (!(catname in this._palette)) {
                this._palette[catname] = size(this._palette);
                this._categories[catname] = Category(catname, 0, currency);
                this._$categories.append(this._categories[catname].$elem);
            }
            var cat = this._categories[catname];

            cat.addAmount(exp.amount);
            if (exp.updated > this._latestupdate) {
                this._latestupdate = exp.updated;
            }

            // Notify all the categories that a new normalization factor has
            // been set.
            if (cat.amount > this._maxamount) {
                this._maxamount = cat.amount;
            }
            for (catname in this._categories) {
                this._categories[catname].onNormalize(this._maxamount);
            }
        },

        _updateExpense: function(exp) {
            var expense = Expense(exp.amount, '&euro;', exp.category, exp.note,
                    exp.date);
            var put = false;

            if (this._expenses.length != 0) {
                for (var i = 0; i < this._expenses.length; i++) {
                    var curexpense = this._expenses[i];

                    if (expense.date > curexpense.date) {
                        expense.$elem.insertBefore(curexpense.$elem);
                        this._expenses.insert(0, expense);
                        put = true;
                        break;
                    }

                }
            }

            if (!put) {
                this._$expenses.append(expense.$elem);
                this._expenses.push(expense);
                put = true;
            }

            expense.onDisplay();
        },

        _onNewData: function(exp) {
            // XXX ignore expenses not in the current *view*
            this._updateCategory(exp);
            this._updateExpense(exp);
        },

        onNewData: function(data) {
            $.each(data.expenses, function(this_) {
                return function() {
                    this_._onNewData(this);
                };
            }(this));
        },

        renderCurrentMonth: function(month, year) {
            this._$title.html('Expenses, ' + month + ' ' + year);
        },

        getPalette: function(category) {
            return this._palette[category];
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
    return function(amount, currency, catname, note, date) {
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
    '<span class="exp_date">' + ui.formatDate(date) + '</span>' +
'</div>'
                ),

            onDisplay: function() {
                var oldbackground = this.$elem.css('backgroundColor');

                this.$elem.css('backgroundColor', '#ffff9c');
                this.$elem.delay(1000).animate({
                    backgroundColor: oldbackground
                }, 'slow');
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

            addAmount: function(amount_) {
                this.amount += amount_;

                this._onAddAmount();
            },

            _onAddAmount: function() {
                // Cache the value
                if (this._$elem_amount == null) {
                    this._$elem_amount = this.$elem.find('.cat_amount');
                }

                this._$elem_amount.html(ui.formatAmount(this.amount, this.currency));
            },

            onNormalize: function(norm) {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(this_) {
                    return function() {
                        // Cache the value
                        if (this_._$elem_bar == null) {
                            this_._$elem_bar = this_.$elem.find('.cat_bar');
                        }

                        var width = 100 * this_.amount / norm;
                        this_._$elem_bar.animate({
                            width: width + '%',
                        }, ui.__animationtimeout);
                    };
                }(this), 200); // XXX use appropriate timeout
            }
        };
    };
}(ExpensesUI);
