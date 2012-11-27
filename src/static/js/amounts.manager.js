var AmountsManager = (function() {
    var logger = null;
    var refreshtimeout = null;
    var ui = null;

    return {
        onReady: function(logger_, refreshtimeout_, ui_) {
            logger = logger_;
            refreshtimeout = refreshtimeout_;
            ui = ui_;
        },


        _onUpdateSuccess: function(data) {
            ui.onNewData(data);
        },

        _onUpdateError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onUpdate: function() {
            $.ajax({
                url: '/amounts.json',
                type: 'GET',
                dataType: 'json',
                data: {
                    days: 30,
                    latest: ui.getLatestUpdate(),
                },

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onUpdateSuccess(data);
                }, this),

                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onUpdateError(data);
                }, this),
            })
        },
    }
})();
