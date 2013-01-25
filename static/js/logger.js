var Logger = (function() {
    var $data = null;
    var fadeouttimeout = null;

    var message = function(kind, msg, next) {
        $data.html(msg).addClass('alert-' + kind)
            .fadeIn().delay(fadeouttimeout).fadeOut('slow').removeClass('alert' + kind);

        if ((typeof next != undefined) && (next != null)) {
            next();
        }
    };

    return {
        onReady: function($data_, fadeouttimeout_) {
            $data = $data_;
            fadeouttimeout = fadeouttimeout_;
        },

        success: function(msg, next) {
            message('success', msg, next);
        },

        error: function(msg, next) {
            message('error', msg, next);
        },
    }
})();
