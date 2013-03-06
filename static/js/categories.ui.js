var CategoriesUI = function() {
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
        categories = {};
        latest = '';
    };

    var initChart = function(data) {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $chart[0].id,
                type: 'pie',
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
                        "<strong>%s</strong>: %s",
                        c.name, formatter.amount(c.amount, c.currency));
                },
            },
            plotOptions: {
                pie: {
                    allowPointSelect: false,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    showInLegend: true,
                },
            },
            credits: {
                enabled: false,
            },
            series: [{
                name: 'Amount spent',
                data: data
            }]
        });
    };

    var sortByDecreasingAmount = function(obj) {
        return -obj.amount;
    };

    var preparePoint = function(indexCategoryArray) {
        var index = indexCategoryArray[0];
        var category = indexCategoryArray[1];

        return {
            name: category.name,
            y: category.amount,
            color: palette.background(category.name),
            obj: category,
        };
    };

    var prepareData = function(categories) {
        return (
            _.filter(
                _.map(
                    _.zip(_.range(1, _.size(categories) + 1), _.values(categories)),
                    preparePoint),
                function(p) { return p.y > 0; }));
    };

    var addPoint = function(_) {
        chart.series[0].addPoint(0);
    };

    var removePoint = function(_) {
        chart.series[0].data[0].remove();
    };

    var updatePoint = function(indexPointArray) {
        var i = indexPointArray[0];
        var point = indexPointArray[1];

        chart.series[0].data[i].update(point);
    };

    var updateChart = function() {
        var categoriesSortedByAmount =
            _.sortBy(categories, sortByDecreasingAmount);
        var data = prepareData(categoriesSortedByAmount);

        // Lazy initialization
        if (chart === null) {
            initChart(data); // Call this when the container is *visible*!
        } else {
            chart.series[0].setData(data);
        }
    };

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
        if (obj.amount === 0.0) {
            if (prev !== undefined) {
                delete categories[obj.name];
            }
        } else {
            categories[obj.name] = obj;
        }
    };

    return {
        onReady: function(formatter_, palette_, $categories_) {
            formatter = formatter_;
            palette = palette_;
            $categories = $categories_;
            $chart = $categories.find('.categories-chart');
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

            _.map(data, updateCategory);

            if (_.any(categories) === false) {
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
};
