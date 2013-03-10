var PaletteManager = (function() {
    var __help = '<h4>Reloading the page!</h4>'
               + 'A new category has been added to the system';
    var logger = null;
    var onReadySuccess = null;

    var income = '#4484ac';
    var outcome = '#b44b4a';
    var net = '#F89406';

    var categories = {};

    var warnTriggered = false;

    var onCategoryListSuccess = function(data) {
        _.map(data.categories, function(category) {
            categories[category.name] = {
                foreground: category.foreground,
                background: category.background
            };
        });
        console.log(categories);
        onReadySuccess();
    };

    var onCategoryListError = function(data) {
        logger.error('Something went wrong while contacting the server');
    };

    var getCategory = function(key) {
        if (categories.hasOwnProperty(key)) {
            return categories[key];
        }

        return { foreground: '#333333', background: '#cccccc' };
    };

    return {
        onReady: function(logger_, onReadySuccess_) {
            logger = logger_;
            onReadySuccess = onReadySuccess_;

            $.ajax({
                dataType: 'json',
                type: 'GET',
                url: '/categories',
                success: onCategoryListSuccess,
                error: onCategoryListError,
            });
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

        net: function() {
            return net;
        },

        foreground: function(key) {
            var color = getCategory(key);

            return color.foreground;
        },

        background: function(key) {
            var color = getCategory(key);

            return color.background;
        },
    };
}());
