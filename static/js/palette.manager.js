var PaletteManager = (function() {
    var logger = null;
    var onReadySuccess = null;

    var chart = '#555555';
    var palette = [
        {bg: '#333',    fg: '#ffe',}, // default
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


    var onCategoryListSuccess = function(data) {
        _.map(data.categories, function(catname) {
            mapping[catname] = _.size(mapping) + 1; // skip default!
        });
        onReadySuccess();
    };

    var onCategoryListError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    return {
        onReady: function(logger_, onReadySuccess_) {
            logger = logger_;
            onReadySuccess = onReadySuccess_;

            init();

            $.ajax({
                dataType: 'json',
                type: 'GET',
                url: '/categories/names',
                success: onCategoryListSuccess,
                error: onCategoryListError,
            });
        },


        get: function(key) {
            if (key in mapping)
                return 1 + (mapping[key] % (palette.length - 1));
            else {
                var msg = '<h4>Reloading the page!</h4>'
                        + 'A new category has been added to the system';
                logger.warn(msg, function() {
                    setTimeout(function() {
                        location.reload();
                    }, 2000);
                });
                return 0;
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
