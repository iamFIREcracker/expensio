var CategoriesManager = (function() {
    var logger = null;
    var refreshtimeout = null;
    var ui = null;
    var timeoutid = null;

    return {
        onReady: function(logger_, refreshtimeout_, ui_) {
            logger = logger_;
            refreshtimeout = refreshtimeout_;
            ui = ui_;
        },


        _onUpdateSuccess: function(data) {
            ui.onNewData(data);

            this.update(refreshtimeout);
        },

        _onUpdateError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        _onUpdate: function() {
            $.ajax({
                url: '/categories.json',
                type: 'GET',
                dataType: 'json',
                data: {
                    year: ui.getYear(),
                    month: ui.getMonth(),
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

        update: function(timeout) {
            if (timeoutid != null) {
                clearTimeout(timeoutid);
            }

            timeoutid = setTimeout(function(_this) {
                _this._onUpdate();
            }, timeout, this);
        },
    }
})();

