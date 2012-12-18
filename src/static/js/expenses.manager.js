var ExpensesManager = (function() {
    var logger = null;
    var date = null;
    var ui = null;
    var addsubmitlisteners = Array();

    var $exp_add = null;

    var onUpdateSuccess = function(data) {
        ui.onNewData(data);
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        setupOnAddSubmit: function($form) {
            $form.submit(function(_this) {
                return function() {
                    return _this.onAddSubmit();
                }
            }(this));
        },

        onReady: function(logger_, date_, ui_) {
            logger = logger_;
            date = date_;
            ui = ui_;
            $exp_add = $('#exp_add');

            this.setupOnAddSubmit($exp_add);
        },


        addSubmit: function(func) {
            addsubmitlisteners.push(func)
        },

        onMonthChange: function(year, month) {
            ui.onMonthChange(year, month);
            this.onUpdate();
        },


        onUpdate: function() {
            var latest = ui.getLatest();
            var data = {
                since: date.getSince(),
                to: date.getTo(),
            }

            if (latest) {
                data['latest'] = latest;
            }

            $.ajax({
                url: '/expenses.json',
                type: 'GET',
                dataType: 'json',
                data: data,
                success: onUpdateSuccess,
                error: onUpdateError,
            });

            return false;
        },


        _onAddSubmitSuccess: function(data) {
            $data = $(data);

            $exp_add.replaceWith($data);
            $exp_add = $('#exp_add');
            this.setupOnAddSubmit($exp_add);

            if ($data.find('.wrong').length == 0) {
                logger.success('Expense tracked successfully!');

                this.onUpdate();

                $.each(addsubmitlisteners, function(index, func) {
                    func();
                });
            }
        },

        _onAddSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onAddSubmit: function() {
            $.ajax({
                url: '/expenses/add',
                type: 'POST',
                dataType: 'html',
                data: $exp_add.serialize(),

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
