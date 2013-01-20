var ExpensesManager = (function() {
    var logger = null;
    var date = null;
    var ui = null;
    var addsubmitlisteners = Array();


    var initWidgets = function() {
        var $date = $('#date');
        if ($date.length) {
            $date.datepicker({
                autoclose: true,
            });   
        }
    };


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
            url: '/expenses',
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


    var onSubmitSuccess = function($form, data, onSuccessCallback) {
        $form.find('.wrong').remove();
        if (!data.success) {
            for (name in data.errors) {
                $form.find('#' + name).parent().append(
                        '<strong class="wrong">' + data.errors[name] + '</strong>');
            }
        } else {
            $form.clearForm();

            onSuccessCallback();
        }
    }


    var onAddSubmitSuccess = function(data) {
        onSubmitSuccess($('#exp_add'), data, function() {
            logger.success('Expense tracked successfully!', function() {
                update();

                $.each(addsubmitlisteners, function(index, func) {
                    func();
                });
            });
        });
    };

    var onAddSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onEditSubmitSuccess = function(data) {
        onSubmitSuccess($('#exp_edit'), data, function() {
            logger.success('Expense edited successfully!', function() {
                setTimeout(function() {
                    window.location = "/";
                }, 2000);
            });
        });
    };

    var onEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onDeleteSubmitSuccess = function(data) {
        logger.success('Expense deleted successfully!', function() {
            update();

            $.each(addsubmitlisteners, function(index, func) {
                func();
            });
        });
    };

    var onDeleteSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onImportSubmitSuccess = function(data) {
        onSubmitSuccess($('#exp_import'), data, function() {
            logger.success('Expenses imported successfully!', function() {
                setTimeout(function() {
                    window.location = "/";
                }, 2000);
            });
        });
    };

    var onImportSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_, date_, ui_) {
            logger = logger_;
            date = date_;
            ui = ui_;

            initWidgets();

            $('#exp_add').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/expenses/add',
                    success: onAddSubmitSuccess,
                    error: onAddSubmitError,
                });

                return false;
            });

            $('#exp_edit').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/expenses/' + $form.find('#id').val() + '/edit',
                    success: onEditSubmitSuccess,
                    error: onEditSubmitError,
                });

                return false;
            });

            $('#exp_import').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/expenses/import',
                    success: onImportSubmitSuccess,
                    error: onImportSubmitError,
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

        onAddExpense: function(exp) {
            exp.$elem.find('.exp_delete').click(function() {
                var $form = $(this);
                var $modal = ui.confirmDelete(exp);

                $modal.find('a').click(function() {
                    $form.ajaxSubmit({
                        dataType: 'json',
                        url: '/expenses/' + $form.find('#id').val() + '/delete',
                        success: onDeleteSubmitSuccess,
                        error: onDeleteSubmitError,
                    });
                });

                return false;
            })
        },

        addSubmit: function(func) {
            addsubmitlisteners.push(func)
        },

    }
})();
