var RecurrencesManager = (function() {
    var logger = null;
    var ui = null;
    var addsubmitlisteners = [];


    var initWidgets = function($context) {
        var $date = $context.find('#yearly');
        if ($date.length) {
            $date.datepicker({
                format: 'mm/dd',
                autoclose: true,
            });
        }
    };


    var update = function() {
        $.ajax({
            url: '/recurrences',
            type: 'GET',
            dataType: 'json',
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
        },

        onUpdate: function() {
            update();
        },

        onAddRecurrence: function(rec) {
            rec.$elem.find('.rec_edit').click(function() {
                var $modal = ui.recurrencesEdit();

                $modal.find('.modal-body').load('/recurrences/' + rec.id + '/edit', function() {
                    initWidgets($modal);

                    $modal.find('#rec_edit').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/recurrences/' + rec.id + '/edit',
                            success: onEditSubmitSuccess,
                            error: onEditSubmitError,
                        });

                        return false;
                    });
                });

                return false;
            });

            rec.$elem.find('.rec_delete').click(function() {
                var $modal = ui.recurrencesDelete();

                $modal.find('.modal-body').load('/recurrences/' + rec.id + '/delete', function() {
                    $modal.find('#rec_delete').submit(function() {
                        var $form = $(this);

                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: '/recurrences/' + rec.id + '/delete',
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

    };
}());
