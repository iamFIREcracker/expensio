var DaysManager = (function() {
    var logger = null;
    var ui = null;
    var paramsFactory = null;

    var onUpdateSuccess = function(data) {
        ui.onNewData(data);
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, ui_, paramsFactory_) {
            logger = logger_;
            ui = ui_;
            paramsFactory = paramsFactory_;
        },


        onUpdate: function() {
            $.ajax({
                url: '/stats/days',
                type: 'GET',
                dataType: 'json',
                data: paramsFactory.get(),
                success: onUpdateSuccess,
                error: onUpdateError,
            });

            return false;
        },
    };
}());
