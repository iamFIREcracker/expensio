function size(obj) {
    var size = 0, key;

    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }

    return size;
}


var AmountsUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var _$days = null;

    var _maxdayamount = null;
    var _days = null;
    var _latestupdate = null;

    return {
        onReady: function($days) {
            _$days = $days;

            this._init();
        },

        _init: function() {
            _$days.empty();
            _days = Array();
            _maxdayamount = 0.0;
            _latestupdate = '1970-01-01 00:00:00.000000'; // epoch

            for (var i = 0; i < 30; i++) {
                var d = Day('', 0, '');

                _days.push(d);
                _$days.append(d.$elem);
            }
        },

        getLatestUpdate: function() {
            return _latestupdate;
        },

        getMaxDayAmount: function() {
            return _maxdayamount;
        },

        _updateDay: function(day) {
            var currency = day.currency;

            _days[day.delta + 29].setAmount(day.amount);

            if (day.amount > _maxdayamount) {
                _maxdayamount = day.amount;
            }

            // Notify all the days that a new normalization factor has
            // been set.
            for (var i = 0; i < 30; i++) {
                _days[i].onDisplay();
            }
        },

        onNewData: function(data) {
            $.each(data.days, function(this_) {
                return function() {
                    this_._updateDay(this);
                }
            }(this));
        },
    };
})();


var Day = function(ui) {
    return function(date, amount, currency) {
        return {
            date: date,
            amount: amount,
            currency: currency,
            $elem: $('' +
'<div class="day_container">' +
    '<div class="day" style="height: 0%">&nbsp;</div>' +
'</div>'
                ),
            _$elem_bar: null,
            _timeoutid: null,

            setAmount: function(amount_) {
                this.amount = amount_;

                //this._onSetAmount();
            },

            //_onSetAmount: function() {
                //// Cache the value
                //if (this._$elem_amount == null) {
                    //this._$elem_amount = this.$elem.find('.cat_amount');
                //}

                //this._$elem_amount.html(ui.formatAmount(this.amount, this.currency));
            //},

            onDisplay: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(this_) {
                    return function() {
                        // Cache the value
                        if (this_._$elem_bar == null) {
                            this_._$elem_bar = this_.$elem.find('.day');
                        }

                        var height = 100 * this_.amount / ui.getMaxDayAmount();
                        this_._$elem_bar.animate({
                            height: height + '%',
                        }, ui.__animationtimeout);
                    };
                }(this), ui.__beforeanimatetimeout);
            }

            
        };
    };
    
}(AmountsUI);
