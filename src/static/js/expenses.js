var ExpensesManager = (function() {
    return {
        _logger: null,
        _refreshtimeout: null,
        _ui: null,
        _timeoutid: null,

        onReady: function(logger, refreshtimeout, ui) {
            this._logger = logger;
            this._refreshtimeout = refreshtimeout;
            this._ui = ui;

            this.update(0);
        },

        update: function(timeout) {
            if (this._timeoutid != null) {
                clearTimeout(this._timeoutid);
            }

            this._timeoutid = setTimeout(function(this_) {
                return function() {
                    this_._onUpdate();
                };
            }(this), timeout);
        },

        _onUpdate: function() {
            $.ajax({
                url: '/expenses.json',
                type: 'GET',
                dataType: 'json',
                data: {
                    year: this._ui.getYear(),
                    month: this._ui.getMonth(),
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

                            this_.update()
                        }
                    };
                }(this),
                error: function(this_) {
                    return function(data) {
                        this_._logger
                            .error('Something went wrong while contacting the server');
                    };
                }(this),
            });

            return false;
        },

        previousMonth: function() {
            this._ui.onPreviousMonth();
            this.update();
        },

        nextMonth: function() {
            this._ui.onNextMonth();
            this.update();
        }
    }
})();
