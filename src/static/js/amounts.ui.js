var AmountsUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds
    var __daysnumber = 30;

    var _$days = null;

    var _maxdayamount = null;
    var _days = null;
    var _latestupdate = null;

    return {
        _init: function() {
            _$days.empty();
            _days = Object();
            _maxdayamount = 0.0;
            _latestupdate = '';

            for (var i = 0; i < __daysnumber; i++) {
                var d = Day('', 0, '');

                _$days.append(d.$elem);
                _days[i] = d;
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


        _updateMaxAmount: function() {
            _maxdayamount = 0;
            for (var i in _days) {
                var curday = _days[i];

                if (curday.amount > _maxdayamount) {
                    _maxdayamount = curday.amount;
                }
            }
        },

        _updateDay: function(obj) {
            var i = obj.delta + __daysnumber - 1;
            var prev = _days[i];

            /*
             * Update the latest received update marker, to send to the server
             * to synchronize exchanged messages.
             */
            if (obj.updated > _latestupdate) {
                _latestupdate = obj.updated;
            }

            /*
             * Remove the previous day element: it will be replaced later on.
             */
            prev.remove();
            delete _days[i];

            /*
             * Create a new Day object, and place it in the right position.
             */
            var newday = Day(obj.date, obj.amount, obj.currency);
            if (i == __daysnumber - 1) {
                _$days.append(newday.$elem);
            } else {
                newday.$elem.insertBefore(_days[i + 1].$elem);
            }
            _days[i] = newday;

            /*
             * Update the changed value of max amount.
             */
            this._updateMaxAmount();

            /*
             * Trigger animations.
             */
            for (var j in _days) {
                _days[j].onDisplay();
            }
        },

        onNewData: function(data) {
            $.each(data.days, EachCallbackWrapper(function(i, value, _this) {
                _this._updateDay(value);
            }, this));
        },


        formatTooltip: function(date, amount, currency) {
            return sprintf("Date: %s Amount: %f %s", date, amount, currency);
        }
    };
})();


var Day = function(ui) {
    return function(date, amount, currency) {
        var obj = {
            date: date,
            amount: amount,
            currency: currency,
            $elem: $('' +
'<div class="day">' +
    '<a class="day_tooltip" href="#" tooltip-data="' + ui.formatTooltip(date, amount, currency) + '">' +
        '<span class="day_bar_container">' +
            '<span class="day_bar" style="height: 0%">&nbsp;</span>' +
        '</span>' +
    '</a>' +
'</div>'
                ),

            _$elem_tooltip: null,
            _$elem_bar: null,
            _timeoutid: null,


            remove: function() {
                this.$elem.remove();
            },

            _onGracefulRemove: function() {
                this.$elem.find('.day_bar').animate({
                    height: 0 + '%',
                }, ui.__animationtimeout).remove();
            },

            gracefulRemove: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onGracefulRemove();
                }, ui.__beforeanimatetimeout, this);
            },


            _onHoverIn: function() {
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

            _onHoverOut: function() {
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

        obj.$elem.hover(function(_this) {
            return function(eventObject) {
                if (_this.amount != 0.0) {
                    _this._onHoverIn();
                }
            };
        }(obj), function(_this) {
            return function(eventObject) {
                if (_this.amount != 0.0) {
                    _this._onHoverOut();
                }
            };
        }(obj))

        return obj;
    };
}(AmountsUI);
