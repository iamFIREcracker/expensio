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
'<div class="control-group error help-inline">' +
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
        onSuccessCallback();
    }
};


/**
 * Swap the sign of the amount of the input category.
 */
var SwapAmountSign = function(c) {
  var r = $.extend({}, c);

  r.amount = -r.amount;
  return r;
};

/**
 * Return true if the current category have a positive amount.
 */
var PositiveAmount = function(c) {
    return c.amount >= 0;
};

/**
 * Return true if the current day has values of income or outcome different from
 * zero.
 */
var WithIncomeOrOutcomeNotNulls = function(d) {
    console.log(d.income, d.outcome, d.income < 0 || d.outcome > 0);
    return d.income < 0 || d.outcome > 0;
};
