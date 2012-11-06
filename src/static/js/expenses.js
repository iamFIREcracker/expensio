var ExpensesManager = (function() {
    return {
        onAddSubmit: function(form) {
            $form = $(form);
            $.ajax({
                url: '/expenses/add',
                type: 'POST',
                dataType: 'html',
                data: $form.serialize(),
                success: function(data) {
                    $data = $(data);
                    $form.replaceWith($data);
                    if ($data.find('.wrong').length == 0) {
                        $('#message').html('Expense tracked successfully!').hide()
                            .fadeIn().delay(2000).fadeOut('slow');
                    }
                },
                error: function(data) {
                    $('#message').html('Ooops! :-(').hide()
                            .fadeIn().delay(2000).fadeOut('slow');
                },
            });

            return false;
        },
    }
})();
