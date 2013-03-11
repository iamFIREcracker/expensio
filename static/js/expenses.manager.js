var ExpensesManager = (function() {
    var logger = null;
    var ui = null;
    var date = null;
    var addsubmitlisteners = [];
    var changecategorylisteners = [];


    var initWidgets = function($context) {
        var $date = $context.find('#date');
        if ($date.length) {
            $date.datepicker({
                autoclose: true,
            }).on('show', function(ev) {
                if (this.value == '') {
                    $(this).datepicker('update', 'today');
                }
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


    var onAddSubmitSuccess = function(data) {
        var $modal = $('.modal');
        var $form = $modal.find('#exp_add');

        OnSubmitSuccess($form, data, function() {
            $modal.on('hidden', function() {
                logger.success('Expense tracked successfully!', function() {
                    $.each(addsubmitlisteners, function(index, func) {
                        func();
                    });
                });
            }).modal('hide');
        });
    };

    var onAddSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onEditSubmitSuccess = function(data) {
        var $modal = $('.modal');
        var $form = $modal.find('#exp_edit');

        OnSubmitSuccess($('#exp_edit'), data, function() {
            $modal.on('hidden', function() {
                logger.success('Expense edited successfully!', function() {
                    $.each(addsubmitlisteners, function(index, func) {
                        func();
                    });
                });
            }).modal('hide');
        });
    };

    var onEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onDeleteSubmitSuccess = function(data) {
        var $modal = $('.modal');
        var $form = $modal.find('#exp_delete');

        OnSubmitSuccess($form, data, function() {
            $modal.on('hidden', function() {
                logger.success('Expense deleted successfully!', function() {
                    $.each(addsubmitlisteners, function(index, func) {
                        func();
                    });
                });
            }).modal('hide');
        });
    };

    var onDeleteSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onImportSubmitSuccess = function(data) {
        var $form = $('#exp_import');
        OnSubmitSuccess($form, data, function() {
            $form.clearForm();
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


    var onExportCheckStatusSuccess = function(data) {
        if (!data.success) {
            setTimeout(function() {
                exportCheckStatus(data.goto);
            }, 1000);
        } else {
            window.location.href = data.goto;
        }
    };

    var onExportCheckStatusError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    var exportCheckStatus = function(url) {
        $.ajax({
            dataType: 'json',
            url: url,
            success: onExportCheckStatusSuccess,
            error: onExportCheckStatusError,
        });
    };

    var onExportSubmitSuccess = function(data) {
        var $form = $('#exp_export');
        OnSubmitSuccess($form, data, function() {
            $form.clearForm();
            logger.info('Waiting for the server to generate export file...', function() {
                exportCheckStatus(data.goto);
            });
        });
    };

    var onExportSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onCategoryEditSubmitSuccess = function(data) {
        var $modal = $('.modal');
        var $form = $modal.find('#category_edit');

        OnSubmitSuccess($('#category_edit'), data, function() {
            $modal.on('hidden', function() {
                $.each(changecategorylisteners, function(index, func) {
                    func();
                });
            }).modal('hide');
        });
    };

    var onCategoryEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_, ui_, date_) {
            logger = logger_;
            ui = ui_;
            date = date_;

            $('#exp_new').click(function() {
                var $modal = ui.expensesAdd();

                $modal.find('.modal-body').load('/expenses/add', function() {
                    initWidgets($modal);

                    $modal.find('#exp_add').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/expenses/add',
                            success: onAddSubmitSuccess,
                            error: onAddSubmitError,
                        });

                        return false;
                    });
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
            })

            $('#exp_export').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/expenses/export',
                    success: onExportSubmitSuccess,
                    error: onExportSubmitError,
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
            exp.$elem.find('.exp_category').click(function() {
                var $modal = ui.categoryEdit();

                $modal.find('.modal-body').load('/categories/' + exp.category + '/edit', function() {
                    $modal.find('.color').each(function() {
                        $(this).colorpicker({
                            format: 'hex'
                        });
                    });

                    $modal.find('#category_edit').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/categories/' + $form.find('#name').val() + '/edit',
                            success: onCategoryEditSubmitSuccess,
                            error: onCategoryEditSubmitError,
                        });

                        return false;
                    });
                });

                return false;
            });

            exp.$elem.find('.exp_edit').click(function() {
                var $modal = ui.expensesEdit();

                $modal.find('.modal-body').load('/expenses/' + exp.id + '/edit', function() {
                    initWidgets($modal);

                    $modal.find('#exp_edit').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/expenses/' + exp.id + '/edit',
                            success: onEditSubmitSuccess,
                            error: onEditSubmitError,
                        });

                        return false;
                    });
                });

                return false;
            });

            exp.$elem.find('.exp_delete').click(function() {
                var $modal = ui.expensesDelete();

                $modal.find('.modal-body').load('/expenses/' + exp.id + '/delete', function() {
                    $modal.find('#exp_delete').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/expenses/' + exp.id + '/delete',
                            success: onDeleteSubmitSuccess,
                            error: onDeleteSubmitError,
                        });

                        return false;
                    });
                });

                return false;
            });
        },

        addSubmit: function(func) {
            addsubmitlisteners.push(func);
        },

        changeCategory: function(func) {
            changecategorylisteners.push(func);
        }
    };
}());
