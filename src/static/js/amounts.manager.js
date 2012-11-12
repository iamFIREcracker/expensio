var AmountsManager = (function() {
    return {
        _logger: null,
        _refreshtimeout: null,
        _ui: null,
        _timeoutid: null,

        onReady: function(logger, refreshtimeout, ui) {
            this._logger = logger;
            this._refreshtimeout = refreshtimeout;
            this._ui = ui;
        },

        update: function(timeout) {
            if (this._timeoutid != null) {
                clearTimeout(this._timeoutid);
            }

            console.log('Schedule new amounts-manager update');
            this._timeoutid = setTimeout(function(this_) {
                return function() {
                    this_._onUpdate();
                };
            }(this), timeout);
        },

        _onUpdate: function() {
            console.log('Amounts manager on update');
            $.ajax({
                url: '/amounts.json',
                type: 'GET',
                dataType: 'json',
                data: {
                    days: 30,
                    latest: this._ui.getLatestUpdate(),
                },
                success: function(this_) {
                    return function(data) {
                        this_._ui.onNewData(data);

                        this_.update(this_._refreshtimeout);
                    };
                }(this),
                error: function(this_) {
                    return function(data) {
                        this_._logger
                            .error('Something went wrong while contacting the server');
                    };
                }(this),
            })
        },
    }
})();
