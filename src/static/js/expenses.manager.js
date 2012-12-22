var ExpensesManager = (function() {
    var logger = null;
    var date = null;
    var ui = null;
    var addsubmitlisteners = Array();

    var update = function() {
        var latest = ui.getLatest();
        var data = {
            since: date.startofcurrentmonth(),
            to: date.endofcurrentmonth(),
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
    };


    var onUpdateSuccess = function(data) {
        ui.onNewData(data);
    };

    var onUpdateError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onAddSubmitSuccess = function(data) {
        var $data = $(data).children();
        var $form = $('#exp_add');

        $form.children().replaceWith($data);
        if ($data.find('.wrong').length == 0) {
            logger.success('Expense tracked successfully!');

            update();

            $.each(addsubmitlisteners, function(index, func) {
                func();
            });
        }
    };

    var onAddSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onEditSubmitSuccess = function(data) {
        var $data = $(data).children();
        var $form = $('#exp_edit');

        $form.children().replaceWith($data);
        if ($data.find('.wrong').length == 0) {
            logger.success(
                    'Expense edited successfully!', function() {
                        setTimeout(function() {
                            parent.history.back();
                        }, 2000);
                    });
        }
    };

    var onEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onDeleteSubmitSuccess = function(data) {
        logger.success('Expense deleted successfully!');

        update();

        $.each(addsubmitlisteners, function(index, func) {
            func();
        });
    };

    var onDeleteSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_, date_, ui_) {
            logger = logger_;
            date = date_;
            ui = ui_;

            $('#exp_add').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'html',
                    url: '/expenses/add',
                    success: onAddSubmitSuccess,
                    error: onAddSubmitError,
                });

                return false;
            });

            $('#exp_edit').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'html',
                    url: '/expenses/' + $form.find('#id').val() + '/edit',
                    success: onEditSubmitSuccess,
                    error: onEditSubmitError,
                });

                return false;
            });
        },

        onMonthChange: function(year, month) {
            ui.onMonthChange(year, month);
            update();
        },

        onUpdate: function() {
            update();
        },

        onAddExpense: function($exp) {
            $exp.find('.exp_delete').click(function() {
                var $form = $(this);
                if (window.confirm("Deleting expense")) {
                    $form.ajaxSubmit({
                        dataType: 'html',
                        url: '/expenses/' + $form.find('#id').val() + '/delete',
                        success: onDeleteSubmitSuccess,
                        error: onDeleteSubmitError,
                    });
                }

                return false;
            })

        },

        addSubmit: function(func) {
            addsubmitlisteners.push(func)
        },


        _onImportSubmitSuccess: function(data) {
            var $data = $(data);
            $form.replaceWith($data);
            if ($data.find('.wrong').length == 0) {
                logger.success(
                        'Expenses imported successfully!', function() {
                            setTimeout(function() {
                                parent.history.back();
                            }, 2000);
                        });
            }
        },

        _onImportSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onImportSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/import',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onImportSubmitSuccess(data);
                }, this),

                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onImportSubmitError(data);
                }, this),
            });

            return false;
        },
    }
})();
