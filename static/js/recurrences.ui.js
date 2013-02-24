var RecurrencesUI = (function() {
    var formatter = null;
    var palette = null;
    var $help = null;
    var $recurrences = null;
    var $inner = null;
    var recurrences = null;
    var addrecurrencelisteners = [];


    var init = function() {
        $inner.empty();
        $recurrences.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        recurrences = {};
    };

    var updateRecurrence = function(obj) {
        var newrec = Recurrence(
            obj.id, obj.yearly, obj.monthly, obj.weekly, obj.category,
            obj.note, obj.amount, obj.currency);
        $inner.append(newrec.$elem);
        recurrences[newrec.id] = newrec;

        /*
         * Trigger animations and notify listeners
         */
        $.each(addrecurrencelisteners, function(index, func) {
            func(newrec);
        });
    };

    return {
        onReady: function(formatter_, palette_, $recurrences_) {
            formatter = formatter_;
            palette = palette_;
            $recurrences = $recurrences_;
            $inner = $recurrences.find('#recurrences-inner');
            $help = $recurrences.find('.alert');

            init();
        },

        onNewData: function(data) {
            var $loading = $recurrences.find('.loading');

            if ($loading.length) {
                $loading.remove();
            }

            _.map(data.recurrences, updateRecurrence);

            if (_.any(recurrences) == false) {
                $inner.hide();
                $help.show();
            } else {
                $help.hide();
                $inner.show();
            }
        },

        recurrencesAdd: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Add recurrence</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        recurrencesEdit: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Edit recurrence</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        recurrencesDelete: function() {
            return $('' +
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Delete recurrence</h3>' +
  '</div>' +
  '<div class="modal-body">' +
  '</div>' +
'</div>'
            ).modal();

        },

        addRecurrence: function(func) {
            addrecurrencelisteners.push(func);
        },
    };
}());


var Recurrence = (function(ui, palette, formatter) {
    return function(id, yearly, monthly, weekly, category, note, amount, currency) {
        var when = function(yearly, monthly, weekly) {
            var msg;

            if (yearly) {
                msg = sprintf("Every <strong>%s</strong>", formatter.yearly(yearly));
            } else if (monthly) {
                msg = sprintf("The <strong>%s</strong> of the month", formatter.monthly(monthly));
            } else if (weekly){
                msg = sprintf("On <strong>%s</strong>", weekly);
            } else {
                msg = "‒";
            }

            return '<span class="rec_when">' + msg + '</span>';
        };

        return {
            id: id,
            yearly: yearly,
            monthly: monthly,
            weekly: weekly,
            category: category,
            note: note,
            amount: amount,
            currency: currency,
            $elem: $(
'<div class="rec">' +
    when(yearly, monthly, weekly) +
    '<span class="rec_inner">' +
        '<span class="rec_category palette" ' +
            'style="background-color: '+ palette.background(category) + '; ' +
                'color: ' + palette.foreground(category) + '">' +
                category +
        '</span>' +
        '<span class="rec_note">' + note + '</span>' +
    '</span>' +
    '<span class="rec_amount">' + formatter.amount(amount, currency) + '</span>' +
    '<span class="rec_edit">' +
        '<a href="/recurrences/' + id + '/edit" title="Edit recurrence">' +
            '<i class="icon-pencil"></i>' +
        '</a>' +
    '</span>' +
    '<span class="rec_delete">' +
        '<a href="/recurrences/' + id + '/delete" title="Delete recurrence">' +
            '<i class="icon-remove"></i>' +
        '</a>' +
    '</span>' +
'</div>'
                ),
        };
    };
}(RecurrencesUI, PaletteManager, Formatter));
