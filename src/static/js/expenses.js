var ExpensesManager = (function() {
    return {
        _logger: null,
        _refreshtimeout: null,
        _ui: null,
        _latestupate: null,

        onReady: function(logger, refreshtimeout, ui) {
            this._logger = logger;
            this._refreshtimeout = refreshtimeout;
            this._ui = ui;
            this._latestupdate = "";
            this._onTimeout();
        },

        _onTimeout: function() {
            $.ajax({
               url: '/expenses.json',
                type: 'GET',
                dataType: 'json',
                success: function(this_) {
                    return function(data) {
                        this_._ui.onNewData(data);
                        //setTimeout(function(this_) {
                            //return function() {
                                //this_._onTimeout();
                            //};
                        //}(this_), this_._refreshtimeout);
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

        onAddSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/add',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),
                success: function(this_) {
                    return function(data) {
                        $data = $(data);
                        $form.replaceWith($data);
                        if ($data.find('.wrong').length == 0) {
                            this_._logger.error('Expense tracked successfully!');
                        }
                    };
                }(this),
                error: function(this_) {
                    return function(data) {
                        this_._logger.error('Oppps! :-(');
                    };
                }(this),
            });

            return false;
        },
    }
})();
