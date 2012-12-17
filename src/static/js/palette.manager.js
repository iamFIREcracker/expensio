var PaletteManager = (function() {
    var palette = null;

    return {
        onReady: function() {
            palette = Object();
        },


        get: function(key) {
            if (key in palette)
                return palette[key];
            else {
                palette[key] = size(palette);
                return palette[key]
            }
        }
    }
})();
