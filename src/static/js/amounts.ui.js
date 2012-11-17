var AmountsUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var _$days = null;

    var _maxdayamount = null;
    var _days = null;
    var _latestupdate = null;

    return {
        _init: function() {
            _$days.empty();
            _days = Array();
            _maxdayamount = 0.0;
            _latestupdate = '1970-01-01 00:00:00.000000'; // epoch

            for (var i = 0; i < 30; i++) {
                var d = Day('', 0, '');

                d.$elem.hover(function(this_) {
                    return function(eventObject) {
                        if (this_.date !== '') {
                            this_.onHoverIn();
                        }
                    };
                }(d), function(this_) {
                    return function(eventObject) {
                        if (this_.date !== '') {
                            this_.onHoverOut();
                        }
                    };
                }(d));

                _days.push(d);
                _$days.append(d.$elem);
            }
        },

        onReady: function($days) {
            _$days = $days;

            this._init();
        },


        getLatestUpdate: function() {
            return _latestupdate;
        },

        getMaxDayAmount: function() {
            return _maxdayamount;
        },


        _onNewData: function(day) {
            var currency = day.currency;
            var d = _days[day.delta + 29];

            d.setDate(day.date);
            d.setAmount(day.amount);
            d.setCurrency(day.currency);

            if (day.amount > _maxdayamount) {
                _maxdayamount = day.amount;
            }

            if (day.updated > _latestupdate) {
                _latestupdate = day.updated;
            }

            // Notify all the days that a new normalization factor has
            // been set.
            for (var i = 0; i < 30; i++) {
                _days[i].onDisplay();
            }
        },

        onNewData: function(data) {
            $.each(data.days, EachCallbackWrapper(function(i, value, _this) {
                _this._onNewData(value);
            }, this));
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
'<div class="day">' +
    '<a class="day_tooltip" href="#" tooltip-data="">' +
        '<span class="day_bar_container">' +
            '<span class="day_bar" style="height: 0%">&nbsp;</span>' +
        '</span>' +
    '</a>' +
'</div>'
                ),
            _$elem_tooltip: null,
            _$elem_bar: null,
            _timeoutid: null,

            setDate: function(date_) {
                this.date = date_;

                this._onValueChange();
            },

            setAmount: function(amount_) {
                this.amount = amount_;

                this._onValueChange();
            },

            setCurrency: function(currency_) {
                this.currency = currency_;

                this._onValueChange();
            },

            _onValueChange: function() {
                this.$elem.find('.day_tooltip').attr(
                        {'tooltip-data': "Date: " + this.date + " " +
                                         "Amount: " + this.amount + " " + this.currency});
            },

            onHoverIn: function() {
                // Cache the value
                if (this._$elem_bar == null) {
                    this._$elem_bar = this.$elem.find('.day_bar');
                }
                if (this._$elem_tooltip == null) {
                    this._$elem_tooltip = this.$elem.find('.day_tooltip');
                }

                this._$elem_bar.addClass('day_bar_hover');
                this._$elem_tooltip.addClass('day_tooltip_hover');
            },

            onHoverOut: function() {
                // Cache the value
                if (this._$elem_bar == null) {
                    this._$elem_bar = this.$elem.find('.day_bar');
                }
                if (this._$elem_tooltip == null) {
                    this._$elem_tooltip = this.$elem.find('.day_tooltip');
                }

                this._$elem_bar.removeClass('day_bar_hover');
                this._$elem_tooltip.removeClass('day_tooltip_hover');
            },

            onDisplay: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(this_) {
                    return function() {
                        // Cache the value
                        if (this_._$elem_bar == null) {
                            this_._$elem_bar = this_.$elem.find('.day_bar');
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
