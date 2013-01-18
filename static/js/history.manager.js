var HistoryManager = (function() {

    var datemanager = null;

    return {
        onReady: function(datemanager_) {
            datemanager = datemanager_;
        },

        onMonthChange: function(year, month) {
            var period = datemanager.period();
            var curperiod = sprintf('%d-%02d', year, month)
            var url = period == curperiod ? '/' : sprintf('/%d/%02d', year, month);
            history.pushState(null, curperiod, url);
        },
    };

})();

