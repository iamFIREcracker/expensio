var ExpensesManager = (function() {
    return {
        _latestupate: null,
        _refreshtimeout: null,
        _logger: null,

        onReady: function(logger, refreshtimeout) {
            this._latestupdate = "";
            this._logger = logger;
            this._refreshtimeout = refreshtimeout;
            this._onTimeout();
        },

        _onTimeout: function() {
            $.ajax({
                url: '/expenses',
                type: 'GET',
                dataType: 'html',
                success: function(_this) {
                    return function(data) {
                        onNewData(data);
                        setTimeout(this._onTimeout, refreshtimeout);
                    }
                }(this),
                error: function(_this) {
                    return function(data) {
                        console.debug(this._logger);
                        _this._logger.error('Ooops! :-(');
                    }
                }(this),
            })
        },

        onAddSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/add',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),
                success: function(_this) {
                    return function(data) {
                        $data = $(data);
                        $form.replaceWith($data);
                        if ($data.find('.wrong').length == 0) {
                            _this._logger.error('Expense tracked successfully!');
                        }
                    }
                }(this),
                error: function(_this) {
                    return function(data) {
                        _this._logger.error('Oppps! :-(');
                    }
                }(this),
            });

            return false;
        },
    }
})();
