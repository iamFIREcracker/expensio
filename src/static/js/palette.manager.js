var PaletteManager = (function() {
    var chart = '#555';
    var palette = [
        {bg: 'red', fg: 'white',},
        {bg: 'orange', fg: 'white',},
        {bg: 'yellow', fg: 'black',},
        {bg: 'green', fg: 'white',},
        {bg: 'blue', fg: 'white',},
        {bg: 'indigo', fg: 'white',},
        {bg: 'violet', fg: 'white',},
    ];
    var mapping = null;

    var init = function() {
        mapping = Object();
    };

    return {
        onReady: function() {
            init();
        },

        onMonthChange: function() {
            init();
        },


        get: function(key) {
            if (key in mapping)
                return mapping[key];
            else {
                mapping[key] = size(mapping);
                return mapping[key]
            }
        },

        chart: function() {
            return chart;
        },

        foreground: function(key) {
            var i = this.get(key);

            return palette[i].fg;
        },

        background: function(key) {
            var i = this.get(key);

            return palette[i].bg;
        },
    }
})();
