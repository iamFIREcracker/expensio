var RecurrencesUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

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
        var newrec = Recurrence(obj.id, obj.amount, obj.currency,
                obj.category, obj.note, obj.date, obj.attachment);

        for (var id in recurrences) {
            var currec = recurrences[id];

            if (newrec.date > currec.date) {
                newrec.$elem.insertBefore(currec.$elem);
                recurrences[newrec.id] = newrec;
                break;
            }
        }
        if (!(newrec.id in recurrences)) {
            $inner.append(newrec.$elem);
            recurrences[newrec.id] = newrec;
        }

        /*
         * Trigger animations and notify listeners
         */
        newrec.flash();
        $.each(addrecurrencelisteners, function(index, func) {
            func(newrec);
        })

        return true;
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

            $inner.empty();

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
            addrecurrencelisteners.push(func)
        },
    };
})();


var Recurrence = function(ui, palette, formatter) {
    return function(id, amount, currency, category, note, date, attachment) {
        var addAttachment = function(attachment, note) {
            if (attachment == null)
                return '' +
'<span class="rec_attach">' +
'</span>';
            else
                return '' +
'<span class="rec_attach">' +
    '<a href="' + attachment + '" rel="lightbox" title="' + note + '">' +
        '<i class="icon-file"></i>' +
    '</a>' +
'</span>';
        };

        return {
            id: id,
            amount: amount,
            currency: currency,
            category: category,
            note: note,
            date: date,
            attachment: attachment,
            $elem: $('' +
'<div class="rec">' +
    '<span class="rec_date">' + formatter.date(date) + '</span>' +
    '<span class="rec_inner">' +
        '<span class="rec_category palette" ' +
            'style="background-color: '+ palette.background(category) + '; ' +
                'color: ' + palette.foreground(category) + '">' +
                category +
        '</span>' +
        '<span class="rec_note">' + note + '</span>' +
    '</span>' +
    '<span class="rec_amount">' + formatter.amount(amount, currency) + '</span>' +
    addAttachment(attachment, note) +
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
            _timeoutid: null,


            remove: function() {
                this.$elem.remove();
            },

            _onGracefulRemove: function() {
                this.$elem.fadeOut('slow', function(_this) {
                    return function() {
                        _this.remove();
                    }
                }(this));
            },

            gracefulRemove: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onGracefulRemove();
                }, ui.__beforeanimatetimeout, this);
            },


            _onFlash: function() {
                this.$elem.addClass('flash')
                    .delay(ui.__animationtimeout).removeClass('flash', 'slow');
            },

            flash: function() {
                if (this._timeoutid != null) {
                    clearInterval(this._timeoutid);
                }

                this._timeoutid = setTimeout(function(_this) {
                    _this._onFlash();
                }, ui.__beforeanimatetimeout, this);
            },
        };
    };
}(RecurrencesUI, PaletteManager, Formatter);
