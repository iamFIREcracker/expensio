function AjaxCallbackWrapper(func, udata) {
    return function(data) {
        func(data, udata);
    };
}

function EachCallbackWrapper(func, data) {
    return function(i, value) {
        func(i, value, data);
    }
}

function size(obj) {
    var size = 0, key;

    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }

    return size;
}



/**
 * Generic handler to manage form submit callbacks.
 */
var OnSubmitSuccess = function($form, data, onSuccessCallback) {
    $form.find('.error').removeClass('error');
    $form.find('.help-inline').remove();
    if (!data.success) {
        if (data.reason) {
            $form.prepend(
'<div class="control-group error">' +
    '<div class="controls">' +
        '<span class="help-inline">' + data.reason + '</span>' +
    '</div>' +
'</div>');
        }
        for (name in data.errors) {
            $field = $form.find('#' + name);
            $field.parent().parent().addClass('error');
            $field.parent().append(
                    '<span class="help-inline">' + data.errors[name] + '</span>');
        }
    } else {
        $form.clearForm();

        onSuccessCallback();
    }
}
