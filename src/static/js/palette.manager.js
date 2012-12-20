var PaletteManager = (function() {
    var chart = '#555555';
    var palette = [
        {bg: '#FF1919', fg: '#ffe',}, // red
        {bg: '#FF9C19', fg: '#222',}, // orange
        {bg: '#FFE819', fg: '#222',}, // yellow
        {bg: '#10A510', fg: '#ffe',}, // blue
        {bg: '#3333FF', fg: '#ffe',},
        {bg: 'indigo',  fg: '#ffe',},
        {bg: 'violet',  fg: '#ffe',},
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
                return mapping[key] % palette.length;
            else {
                mapping[key] = size(mapping);
                return mapping[key] % palette.length;
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
