var UsersManager = (function() {
    var logger = null;
    var ui = null;


    var onAvatarRemoveSubmitSuccess = function(data) {
        logger.success(
                'Avatar successfully removed!', function() {
                    window.location.reload();
                });
    };

    var onAvatarRemoveSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };



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
        onReady: function(logger_, ui_) {
            logger = logger_;
            ui = ui_;

            $('#user_avatar #choose').click(function() {
                alert('Choose');
            });

            $('#user_avatar #remove').click(function() {
                var $remove = $(this);
                var $form = $remove.closest('form');
                console.log($form);
                var $modal = ui.confirmAvatarRemove();

                $modal.find('a').click(function() {
                    $form.ajaxSubmit({
                        dataType: 'json',
                        url: '/users/' + $form.find('#id').val() + '/avatar/remove',
                        success: onAvatarRemoveSubmitSuccess,
                        error: onAvatarRemoveSubmitError,
                    });
                });
            });

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
    };
}());
