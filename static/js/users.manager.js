var UsersManager = (function() {
    var logger = null;


    var onEditSubmitSuccess = function(data) {
        var $data = $(data).children();
        var $form = $('#user_edit');

        $form.children().replaceWith($data);
        if ($data.find('.wrong').length == 0) {
            logger.success(
                    'User edited successfully!', function() {
                        setTimeout(function() {
                            window.location = '/';
                        }, 2000);
                    });
        }
    };

    var onEditSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_) {
            logger = logger_;

            $('#user_edit').submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'html',
                    url: '/users/' + $form.find('#id').val() + '/edit',
                    success: onEditSubmitSuccess,
                    error: onEditSubmitError,
                });

                return false;
            });
        },
    }
})();
