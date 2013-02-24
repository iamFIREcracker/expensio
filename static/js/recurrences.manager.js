var RecurrencesManager = (function() {
    var logger = null;
    var ui = null;
    var addsubmitlisteners = Array();


    var initWidgets = function($context) {
        var $date = $context.find('#yearly');
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
            url: '/recurrences',
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
        var $form = $modal.find('#rec_add');

        OnSubmitSuccess($form, data, function() {
            $modal.on('hidden', function() {
                logger.success('Recurrence tracked successfully!', function() {
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
        var $form = $modal.find('#rec_edit');

        OnSubmitSuccess($('#rec_edit'), data, function() {
            $modal.on('hidden', function() {
                logger.success('Recurrence edited successfully!', function() {
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
        var $form = $modal.find('#rec_delete');

        OnSubmitSuccess($form, data, function() {
            $modal.on('hidden', function() {
                logger.success('Recurrence deleted successfully!', function() {
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
        var $form = $('#rec_import');
        OnSubmitSuccess($form, data, function() {
            $form.clearForm();
            logger.success('Recurrences imported successfully!', function() {
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
        var $form = $('#rec_import');
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


    return {
        onReady: function(logger_, ui_) {
            logger = logger_;
            ui = ui_;

            $('#rec_new').click(function() {
                var $modal = ui.recurrencesAdd();

                $modal.find('.modal-body').load('/recurrences/add', function() {
                    initWidgets($modal);

                    $modal.find('#rec_add').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/recurrences/add',
                            success: onAddSubmitSuccess,
                            error: onAddSubmitError,
                        });

                        return false;
                    });
                });
                return false;
            });

            $('#rec_import').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/recurrences/import',
                    success: onImportSubmitSuccess,
                    error: onImportSubmitError,
                });

                return false;
            })

            $('#rec_export').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/recurrences/export',
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

        onAddRecurrence: function(exp) {
            exp.$elem.find('.rec_edit').click(function() {
                var $modal = ui.recurrencesEdit();

                $modal.find('.modal-body').load('/recurrences/' + exp.id + '/edit', function() {
                    initWidgets($modal);

                    $modal.find('#rec_edit').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/recurrences/' + exp.id + '/edit',
                            success: onEditSubmitSuccess,
                            error: onEditSubmitError,
                        });

                        return false;
                    });
                });

                return false;
            });

            exp.$elem.find('.rec_delete').click(function() {
                var $modal = ui.recurrencesDelete();

                $modal.find('.modal-body').load('/recurrences/' + exp.id + '/delete', function() {
                    $modal.find('#rec_delete').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/recurrences/' + exp.id + '/delete',
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
            addsubmitlisteners.push(func)
        },

    };
}());
