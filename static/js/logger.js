var Logger = (function() {
    return {
        _$data: null,
        _fadeouttimeout: null,

        onReady: function($data, fadeouttimeout) {
            this._$data = $data;
            this._fadeouttimeout = fadeouttimeout;
        },

        success: function(msg, next) {
            this.error(msg);

            if ((typeof next != undefined) && (next != null)) {
                next();
            }
        },

        error: function(msg) {
            this._$data.hide().html(msg).fadeIn()
                    .delay(this._fadeouttimeout).fadeOut('slow');
        }
    }
})();
