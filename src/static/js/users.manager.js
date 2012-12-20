var UsersManager = (function() {
    var logger = null;

    return {
        onReady: function(logger_) {
            logger = logger_;
        },


        _onEditSubmitSuccess: function(data) {
            $data = $(data);
            $form.replaceWith($data);
            if ($data.find('.wrong').length == 0) {
                logger.success(
                        'Users edited successfully!', function() {
                            setTimeout(function() {
                                window.location = '/';
                            }, 2000);
                        });
            }
        },

        _onEditSubmitError: function(data) {
            logger.error('Something went wrong while contacting the server');
        },

        onEditSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/users/' + $form.find('#id').val() + '/edit',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),

                success: AjaxCallbackWrapper(function(data, _this) {
                    _this._onEditSubmitSuccess(data);
                }, this),


                error: AjaxCallbackWrapper(function(data, _this) {
                    _this._onEditSubmitError(data);
                }, this),
            });

            return false;
        },
    }
})();
