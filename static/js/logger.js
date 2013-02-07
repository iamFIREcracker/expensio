var Logger = (function() {
    var $pageAlert = null;
    var fadeouttimeout = null;

    var message = function(kind, msg, next) {
        $pageAlert.html(msg).addClass('alert-' + kind)
            .fadeIn().delay(fadeouttimeout).fadeOut('slow').removeClass('alert' + kind);

        if ((typeof next != undefined) && (next != null)) {
            next();
        }
    };


    return {
        onReady: function($pageAlert_, fadeouttimeout_) {
            $pageAlert = $pageAlert_;
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
