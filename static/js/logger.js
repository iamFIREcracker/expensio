var Logger = (function() {
    var $pageAlert = null;
    var fadeouttimeout = null;
    var tid = null;
    var queue = [];

    var message = function(kind, msg, next) {
        $pageAlert.html(msg).addClass('alert-' + kind)
            .fadeIn().delay(fadeouttimeout).fadeOut('slow', function () {
                $(this).removeClass('alert' + kind);

                if (next !== undefined) {
                    next();
                }

                reschedule();
            });
    };

    var reschedule = function() {
        tid = null;

        if (queue.length) {
            var item = queue.pop(0);

            enqueue(item.kind, item.msg, item.next);
        }
    };

    var enqueue = function(kind, msg, next) {
        if (tid === null) {
            tid = setTimeout(function() {
                message(kind, msg, next);
            });
        } else {
            queue.push({ kind: kind, msg: msg, next: next });
        }
    };


    return {
        onReady: function($pageAlert_, fadeouttimeout_) {
            $pageAlert = $pageAlert_;
            fadeouttimeout = fadeouttimeout_;
        },

        success: function(msg, next) {
            enqueue('success', msg, next);
        },

        warn: function(msg, next) {
            enqueue('warn', msg, next);
        },

        error: function(msg, next) {
            enqueue('error', msg, next);
        }
    };
}());
