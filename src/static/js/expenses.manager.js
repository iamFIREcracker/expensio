var ExpensesManager = (function() {
    var logger = null;
    var refreshtimeout = null;
    var ui = null;
    var timeoutid = null;

    var $exp_add = null;

    return {
        setupOnAddSubmit: function($form) {
            $form.submit(function(_this) {
                return function() {
                    _this.onAddSubmit(this);
                }
            }(this));
        },

        onReady: function(logger_, refreshtimeout_, ui_) {
            logger = logger_;
            refreshtimeout = refreshtimeout_;
            ui = ui_;

            $exp_add = $('#exp_add');

            this.setupOnAddSubmit($exp_add);
        },


        onMonthChange: function(year, month) {
            ui.onMonthChange(year, month);
            this.update();
        },


        _onUpdateSuccess: function(data) {
            ui.onNewData(data);
        },

        _onUpdateError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        _onUpdate: function() {
            $.ajax({
                url: '/expenses.json',
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
            });

            return false;
        },

        update: function(timeout) {
            if (timeoutid != null) {
                clearTimeout(timeoutid);
            }

            timeoutid = setTimeout(function(this_) {
                this_._onUpdate();
            }, timeout, this);
        },


        _onAddSubmitSuccess: function(data) {
            $data = $(data);
            this.$exp_add.replaceWith($data);
            if ($data.find('.wrong').length == 0) {
                logger.success('Expense tracked successfully!');

                this.update()
            }

            this.setupOnAddSubmit($form);
        },

        _onAddSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onAddSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/add',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onAddSubmitSuccess(data);
                }, this),

                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onAddSubmitError(data);
                }, this)
            });

            return false;
        },


        _onEditSubmitSuccess: function(data) {
            $data = $(data);
            $form.replaceWith($data);
            if ($data.find('.wrong').length == 0) {
                logger.success(
                        'Expense edited successfully!', function() {
                            setTimeout(function() {
                                parent.history.back();
                            }, 2000);
                        });
            }
        },

        _onEditSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onEditSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/' + $form.find('#id').val() + '/edit',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onEditSubmitSuccess(data);
                }, this),


                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onEditSubmitError(data);
                }, this),
            });

            return false;
        },


        _onDeleteSubmitSuccess: function(data) {
            $data = $(data);
            $form.replaceWith($data);
            if ($data.find('.wrong').length == 0) {
                logger.success(
                        'Expense deleted successfully!', function() {
                            setTimeout(function() {
                                parent.history.back();
                            }, 2000);
                        });
            }
        },

        _onDeleteSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onDeleteSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/' + $form.find('#id').val() + '/delete',
                type: 'POST',
                dataType: 'html',

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onDeleteSubmitSuccess(data);
                }, this),

                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onDeleteSubmitError(data);
                }, this),
            });

            return false;
        },
    }
})();
