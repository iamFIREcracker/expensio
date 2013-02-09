var UsersManager = (function() {
    var logger = null;

    var onEditSubmitSuccess = function(data) {
        OnSubmitSuccess($('#user_edit'), data, function() {
            logger.success(
                    'User edited successfully!', function() {
                        window.location = '/';
                    });
        });
    };

    var onEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    var onDeleteSubmitSuccess = function(data) {
        logger.success(
                'Account successfully deactivated .. bye byeeee!', function() {
                    window.location = '/';
                });
    };

    var onDeleteSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_) {
            logger = logger_;

            $('#user_edit').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/users/' + $form.find('#id').val() + '/edit',
                    success: onEditSubmitSuccess,
                    error: onEditSubmitError,
                });

                return false;
            });

            $('#user_delete').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'html',
                    url: '/users/' + $form.find('#id').val() + '/delete',
                    success: onDeleteSubmitSuccess,
                    error: onDeleteSubmitError,
                });

                return false;
            });
        },
    }
})();
