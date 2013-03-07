var ParamsManager = (function() {
    var date = null;

    var days = function(mode) {
        var since;

        if (mode === 'life') {
            since = date.epoch();
        } else if (mode === 'year') {
            since = date.ndaysback(365 - 1);
        } else if (mode === 'quadrimester') {
            since = date.ndaysback(120 - 1);
        }

        return {since: since, to: date.today()};
    };

    return {
        onReady: function(date_) {
            date = date_;
        },

        Categories: (function() {
            var latest;
            return {
                get: function() {
                    return {
                        since: date.startofcurrentmonth(),
                        to: date.endofcurrentmonth(),
                        latest: latest
                    };
                },

                onMonthChange: function(year, month) {
                    latest = undefined;
                },

                onNewData: function(categories) {
                    var latest_ = _.last(_.sortBy(categories, function(c) {
                        return c.updated;
                    }));

                    if (latest_ !== undefined &&
                        (latest === undefined || latest_.updated > latest)) {
                        latest = latest_.updated;
                    }
                }

            };
        }()),

        statsDays: function(mode, bins) {
            return {
                get: function() {
                    return $.extend({bins: bins}, days(mode));
                }
            };
        },

        statsCategories: function(mode) {
            return {
                get: function() {
                    return days(mode);
                }
            };
        }
    };
}());
