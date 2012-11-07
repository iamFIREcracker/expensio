var Logger = (function() {
    return {
        _$data: null,
        _fadeouttimeout: null,

        onReady: function($data, fadeouttimeout) {
            this._$data = $data;
            this._fadeouttimeout = fadeouttimeout;
        },

        success: function(msg) {
            this.error(msg);
        },

        error: function(msg) {
            this._$data.html(msg).hide().fadeIn()
                    .delay(this._fadeouttimeout).fadeOut('slow');
        }
    }
})();
