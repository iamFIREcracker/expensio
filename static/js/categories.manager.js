var CategoriesManager = (function() {
    var logger = null;
    var paramsFactory = null;
    var newdatalisteners = [];

    var onUpdateSuccess = function(data) {
        $.each(newdatalisteners, function(index, func) {
            func(data);
        });
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, paramsFactory_) {
            logger = logger_;
            paramsFactory = paramsFactory_;
        },

        onMonthChange: function(year, month) {
            this.onUpdate();
        },

        onUpdate: function() {
            $.ajax({
                url: '/stats/categories',
                type: 'GET',
                dataType: 'json',
                data: paramsFactory.get(),
                success: onUpdateSuccess,
                error: onUpdateError,
            });

            return false;
        },

        newData: function(func) {
            newdatalisteners.push(func);
        },
    };
}());

