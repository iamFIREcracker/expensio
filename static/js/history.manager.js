var HistoryManager = (function() {

    var datemanager = null;

    return {
        onReady: function(datemanager_) {
            datemanager = datemanager_;
        },

        onMonthChange: function(year, month) {
            history.pushState(null, sprintf('%d-%02d', year, month),
                            sprintf('/%d/%02d', year, month));
        },
    };

})();

