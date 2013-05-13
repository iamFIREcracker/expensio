var UsersManager = (function() {
    var logger = null;
    var ui = null;

    var avatarChangeCheckStatus = function(url) {
        $.ajax({
            dataType: 'json',
            url: url,
            statusCode: {
                200: function(data) {
                    setTimeout(function() {
                        avatarChangeCheckStatus(url);
                    }, 1000);
                },
                201: function() {
                    setTimeout(function() {
                        window.location.reload();
                    }, 2000);
                }
            }
        });
    };


    var onAvatarChangeSubmitSuccess = function(data) {
        OnSubmitSuccess($('#user_avatar'), data, function() {
            // Nothing to do here, apart from validation.  The API workflow
            // suggests a '202 Accepted' in case of success.
        });
    };

    var onAvatarChangeSubmitError = function(data) {
        if (data.status === 202 && data.responseText === 'Accepted') {
            logger.info('Waiting for the server to process the image...', function() {
                avatarChangeCheckStatus(data.getResponseHeader('Location'));
            });
        } else {
            logger.error('Something went wrong while contacting the server');
        }
    };


    var onAccountDisconnectSuccess = function(data) {
        OnSubmitSuccess($('#user_connect'), data, function() {
            logger.success(
                    'Account disconnected successfully!', function() {
                        setTimeout(function() {
                            window.location.reload();
                        }, 2000);
                    });
        });
    };

    var onAccountDisconnectError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };


    return {
        onReady: function(logger_, ui_) {
            logger = logger_;
            ui = ui_;

            $('#user_avatar #choose').click(function() {
                var $form = $(this).closest('form');
                var $modal = ui.avatarChange($form.find('#id').val());

                $modal.find('a').click(function() {
                    a = $(this);
                    var $form = $(this).parent().parent().find('form');

                    $form.ajaxSubmit({
                        dataType: 'json',
                        url: '/v1/users/' + $form.find('#id').val() + '/avatar/change',
                        success: onAvatarChangeSubmitSuccess,
                        error: onAvatarChangeSubmitError,
                    });

                    logger.info("Sending avatar to the server...");
                });
            });
            $('#user_avatar #remove').click(function() {
                var $form = $(this).closest('form');
                var $modal = ui.confirmAvatarRemove();

                $modal.find('a').click(function() {
                    $.ajax({
                        dataType: 'json',
                        type: 'POST',
                        url: '/v1/users/' + $form.find('#id').val() + '/avatar/remove',
                        statusCode: {
                            204: function(data) {
                                logger.success(
                                        'Avatar successfully removed!',
                                        function() {
                                            setTimeout(function() {
                                                window.location.reload();
                                            }, 2000);
                                        });
                            },
                        },
                    });
                });
            });

            $('#submit').click(function() {
                $('#user_edit').submit();
            });
            $('#user_edit').submit(function() {
                var $form = $(this);

                $.ajax({
                    dataType: 'json',
                    type: 'POST',
                    url: '/v1/users/' + $form.find('#id').val() + '/edit',
                    data: $form.formSerialize(),
                    statusCode: {
                        200: function(data) {
                            OnSubmitSuccess($('#user_edit'), data);
                        },
                        204: function(data) {
                            logger.success('User edited successfully!');
                        }
                    },
                    
                });

                return false;
            });

            $('#user_connect a').each(function(i) {
                $(this).click(function() {
                    var $anchor = $(this);
                    var $form = $anchor.closest('form');

                    if ($anchor.html() === "Disconnect") {
                        $form.ajaxSubmit({
                            dataType: 'json',
                            url: $anchor.attr('href'),
                            success: onAccountDisconnectSuccess,
                            error: onAccountDisconnectError,
                        });

                        return false;
                    }
                });
            });

            $('#user_delete').submit(function() {
                var $form = $(this);

                $.ajax({
                    dataType: 'json',
                    type: 'POST',
                    url: '/v1/users/' + $form.find('#id').val() + '/delete',
                    statusCode: {
                        204: function(data) {
                            logger.success(
                                    'Account successfully deactivated .. bye byeeee!',
                                    function() {
                                        setTimeout(function() {
                                            window.location = '/';
                                        }, 2000);
                                    });

                        }
                    }
                });

                return false;
            });
        },
    };
}());
