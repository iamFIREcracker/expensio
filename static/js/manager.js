var Manager = (function() {
    var logger = null;
    var refreshtimeout = null;
    var updatelisteners = Array();
    var daychangelisteners = Array();
    var monthchangelisteners = Array();
    var timeoutid = null;

    var curyear = null;
    var curmonth = null;

    return {
        onReady: function(logger_, refreshtimeout_) {
            var date = new Date();

            logger = logger_;
            refreshtimeout = refreshtimeout_;

            curyear = date.getYear() + 1900; // Fix relative to 1900
            curmonth = date.getMonth(); // 0-indexed months

            $('#prev_month').click(function(_this) {
                return function() {
                    _this.onPrevMonth();
                }
            }(this));

            $('#next_month').click(function(_this) {
                return function() {
                    _this.onNextMonth();
                }
            }(this));
        },


        update: function(func) {
            updatelisteners.push(func);
        },

        dayChange: function(func) {
            daychangelisteners.push(func);
        },

        monthChange: function(func) {
            monthchangelisteners.push(func);
        },


        _onUpdate: function() {
            $.each(updatelisteners, function(index, func) {
                func();
            });

            this.onUpdate(refreshtimeout);
        },

        onUpdate: function(timeout) {
            if (timeoutid != null) {
                clearTimeout(timeoutid);
            }

            timeoutid = setTimeout(function(_this) {
                _this._onUpdate();
            }, timeout, this);
        },


        _onMonthChange: function() {
            $.each(monthchangelisteners, function(index, func) {
                func(curyear, curmonth);
            });
        },

        onPrevMonth: function() {
            curmonth -= 1;
            if (curmonth < 0) {
                curmonth = 11;
                curyear -= 1;
            }

            this._onMonthChange();
        },

        onNextMonth: function() {
            curmonth += 1;
            if (curmonth == 12) {
                curmonth = 0;
                curyear += 1;
            }

            this._onMonthChange();
        },
    }
})();
