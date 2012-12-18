var DaysManager = (function() {
    var logger = null;
    var ui = null;

    var onUpdateSuccess = function(data) {
        ui.onNewData(data);
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, ui_) {
            logger = logger_;
            ui = ui_;
        },


        onUpdate: function() {
            var latest = ui.getLatest();
            var data = {
                n: ui.getN(),
            }

            if (latest) {
                data['latest'] = latest;
            }

            $.ajax({
                url: '/days.json',
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
