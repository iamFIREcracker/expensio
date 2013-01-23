var Logger = (function() {
    var $data = null;
    var fadeouttimeout = null;

    return {
        onReady: function($data_, fadeouttimeout_) {
            $data = $data_;
            fadeouttimeout = fadeouttimeout_;
        },

        success: function(msg, next) {
            this.error(msg);

            if ((typeof next != undefined) && (next != null)) {
                next();
            }
        },

        error: function(msg) {
            $data.hide().html(msg).fadeIn()
                    .delay(fadeouttimeout).fadeOut('slow');
        },
    }
})();
