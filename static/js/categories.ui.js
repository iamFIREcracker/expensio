﻿var CategoriesUI = (function() {
    var __animationtimeout = 200; // milliseconds

    var formatter = null;
    var palette = null;
    var $categories = null;
    var $chart = null;
    var $help = null;
    var chart = null;
    var categories = null;
    var latest = null;

    var init = function() {
        $chart.empty().hide();
        $categories.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        chart = null;
        categories = Object();
        latest = '';
    };

    var initChart = function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $chart[0].id,
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false
            },
            title: {
                text: null,
            },
            subtitle: {
                text: null,
            },
            tooltip: {
                formatter: function() {
                    var c = this.point.obj;
                    return sprintf(
                        "%s", formatter.amount(c.amount, c.currency))
                },
            },
            plotOptions: {
                pie: {
                    allowPointSelect: false,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false,
                    },
                    showInLegend: true,
                },
            },
            credits: {
                enabled: false,
            },
            series: [{
                type: 'pie',
                name: 'Amount spent',
                data: [],
            }]
        });
    };

    var preparePoint = function(category) {
        return {
            name: category.name,
            y: category.amount,
            color: palette.background(category.name),
            obj: category,
        };
    }

    var updateChart = function() {
        // Lazy initialization
        if (chart == null) {
            initChart(); // Call this when the container is *visible*!
        }

        chart.series[0].setData(
            _.sortBy(
                _.map(categories, preparePoint),
                function(e) { return -e.y; }));
    }

    var updateCategory = function(obj) {
        var prev = categories[obj.name];

        /*
         * Update the variable containing the date of the latest update.
         * This operation should be done on all received updates, even those
         * representing deleted items.
         */
        if (obj.updated > latest) {
            latest = obj.updated;
        }

        /*
         * The current category is no more valid (amount equal 0.0).  Check
         * for a previously received update: if present, issue a graceful
         * remove, otherwise return.
         */
        if (obj.amount == 0.0) {
            if (prev === undefined) {
                return false;
            } else {
                delete categories[obj.name];
                return true;
            }
        }

        categories[obj.name] = obj;

        return true;
    };

    return {
        onReady: function(formatter_, palette_, $categories_) {
            formatter = formatter_;
            palette = palette_;
            $categories = $categories_;
            $chart = $categories.find('#categories-chart');
            $help = $categories.find('.alert');

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            var $loading = $categories.find('.loading');

            if ($loading.length) {
                $loading.remove();
            }

            _.map(data.stats.categories, updateCategory);

            if (_.any(categories) == false) {
                $chart.hide();
                $help.show();
            } else {
                $help.hide();
                $chart.show();
                updateChart();
            }
        },


        getLatest: function() {
            return latest;
        },
    };
})();
