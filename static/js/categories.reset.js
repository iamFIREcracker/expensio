var CategoriesReset = (function() {
    var logger = null;
    var $form = null;


    var onCheckStatusSuccess = function(data) {
        if (!data.success) {
            setTimeout(function() {
                checkStatus(data.goto);
            }, 1000);
        } else {
            window.location = '/';
        }
    };

    var onCheckStatusError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    var checkStatus = function(url) {
        $.ajax({
            dataType: 'json',
            url: url,
            success: onCheckStatusSuccess,
            error: onCheckStatusError,
        });
    };

    var onResetSubmitSuccess = function(data) {
        OnSubmitSuccess($form, data, function() {
            logger.info('Waiting for the server to reset categories...', function() {
                checkStatus(data.goto);
            });
        });
    };

    var onResetSubmitError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, $form_) {
            logger = logger_;
            $form = $form_;
            
            $form.submit(function() {
                var $form = $(this);

                $form.ajaxSubmit({
                    dataType: 'json',
                    url: '/categories/reset',
                    success: onResetSubmitSuccess,
                    error: onResetSubmitError,
                });

                return false;
            });
        }
    };
}());
