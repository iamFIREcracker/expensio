var PaletteManager = (function() {
    var __help = '<h4>Reloading the page!</h4>'
               + 'A new category has been added to the system';
    var logger = null;
    var onReadySuccess = null;

    var chart = '#555555';
    var income = '#4484ac';
    var outcome = '#b44b4a';
    var palette = [
        {bg: '#333',    fg: '#ffe',}, // default
        {bg: '#3366CC', fg: '#ffe',}, // blue
        {bg: '#dc3912', fg: '#222',}, // red
        {bg: '#ff9900', fg: '#222',}, // yellow
        {bg: '#109618', fg: '#ffe',}, // blue
        {bg: '#990099', fg: '#ffe',},
        {bg: '#0099c6', fg: '#ffe',},
        {bg: '#dd4477', fg: '#ffe',},
    ];
    var mapping = {};
    var warnTriggered = false;

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
                if (!warnTriggered) {
                    warnTriggered = true;

                    logger.warn(__help, function() {
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    });
                }
                return 0;
            }
        },

        chart: function() {
            return chart;
        },

        income: function() {
            return income;
        },

        outcome: function() {
            return outcome;
        },

        foreground: function(key) {
            var i = this.get(key);

            return palette[i].fg;
        },

        background: function(key) {
            var i = this.get(key);

            return palette[i].bg;
        },
    };
}());
