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
 * Return true if the current category has a negative income.
 */
var IncomeNotNull = function(c) {
    return c.income < 0;
};


/**
 * Return true if the current category has a positive outcome.
 */
var OutcomeNotNull = function(c) {
    return c.outcome > 0;
};


/**
 * Return true if the current day has values of income or outcome different from
 * zero.
 */
var WithIncomeOrOutcomeNotNulls = function(d) {
    return d.income < 0 || d.outcome > 0;
};
