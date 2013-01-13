var CategoriesManager = (function() {
    var logger = null;
    var date = null;
    var ui = null;

    var onUpdateSuccess = function(data) {
        ui.onNewData(data);
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, date_, ui_) {
            logger = logger_;
            date = date_;
            ui = ui_;
        },

        onMonthChange: function(year, month) {
            ui.onMonthChange(year, month);
            this.onUpdate();
        },

        onUpdate: function() {
            var latest = ui.getLatest();
            var data = {
                since: date.startofcurrentmonth(),
                to: date.endofcurrentmonth(),
            }

            if (latest) {
                data['latest'] = latest;
            }

            $.ajax({
                url: '/categories.json',
                type: 'GET',
                dataType: 'json',
                data: data,
                success: onUpdateSuccess,
                error: onUpdateError,
            });

            return false;
        },
    }
})();
