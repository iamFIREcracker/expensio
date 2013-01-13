var CategoriesUI = (function() {
    var formatter = null;
    var palette = null;
    var $categories = null;
    var chart = null;
    var categories = null;
    var latest = null;

    var init = function() {
        $categories.html('<div class="loading"><img src="/static/images/loading.gif" /></div>')
        chart = null;
        categories = Object();
        latest = '';
    };

    var initChart = function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $categories[0].id,
                type: 'bar',
                animation: false,
            },
            title: {
                text: null,
            },
            subtitle: {
                text: null,
            },
            xAxis: {
                title: {
                    text: null
                },
            },
            yAxis: {
                min: 0,
                title: {
                    text: null,
                },
                labels: {
                    overflow: 'justify'
                },
            },
            tooltip: {
                enabled: false,
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: true,
                        formatter: function() {
                            var c = this.point.obj;
                            return sprintf(
                                "%s", formatter.amount(c.amount, c.currency))
                        }

                    }
                },
                series: {
                    pointWidth: 20,
                },
            },
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            series: [{
                name: 'Amount',
                data: [],
            }]
        });
    };

    var updateChart = function() {
        /*
         * Chart lazy initialization.
         */
        if (chart == null) {
            initChart();
        }

        var sortable = Array();
        var catnames = Array();
        var catamounts = Array();

        for (var name in categories)
            sortable.push(name);

        sortable.sort();
        for (var i in sortable) {
            var c = categories[sortable[i]]

            catnames.push(c.name);
            catamounts.push({
                y: c.amount,
                color: palette.background(c.name),
                obj: c,
            });
        }

        chart.series[0].setData(catamounts);
        chart.xAxis[0].setCategories(catnames);
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
                return;
            } else {
                delete categories[obj.name];
                return;
            }
        }

        categories[obj.name] = obj;
    };

    return {
        onReady: function(formatter_, palette_, $categories_) {
            formatter = formatter_;
            palette = palette_;
            $categories = $categories_;

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            if ($categories.find('.loading').length) {
                $categories.empty();
            }
            if (data.categories.length) {
                $.each(data.categories, EachCallbackWrapper(function(i, value, _this) {
                    updateCategory(value);
                }, this));

                updateChart();
            }
        },


        getLatest: function() {
            return latest;
        },
    };
})();
