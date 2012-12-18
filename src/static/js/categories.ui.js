var CategoriesUI = (function() {
    var __beforeanimatetimeout = 200;
    var __animationtimeout = 200; // milliseconds

    var palette = null;
    var $categories = null;
    var chart = null;
    var categories = null;
    var latest = null;

    var init = function() {
        $categories.empty();
        chart = null;
        categories = Object();
        latest = '';
    };

    var initChart = function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $categories[0].id,
                type: 'bar',
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
                }
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Amount (€)',
                    align: 'high'
                },
                labels: {
                    overflow: 'justify'
                }
            },
            tooltip: {
                formatter: function() {
                    return ''+
                        this.series.name +': '+ this.y;
                }
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: false
                    }
                }
            },
            legend: {
                enabled: false
            },
            credits: {
                enabled: false
            },
            series: [{
                name: 'Amounts',
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
        console.log(sortable);
        for (var i in sortable) {
            var c = categories[sortable[i]]

            console.log(c);
            catnames.push(c.name);
            catamounts.push(c.amount);
        }

        console.log(categories);
        console.log(catnames, catamounts);
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
        chart: function() { updateChart(); return chart; },
        onReady: function(palette_, $categories_) {
            palette = palette_;
            $categories = $categories_;

            init();
        },

        onMonthChange: function(year, month) {
            init();
        },

        onNewData: function(data) {
            $.each(data.categories, EachCallbackWrapper(function(i, value, _this) {
                updateCategory(value);
            }, this));

            if (data.categories.length)
                updateChart();
        },


        getLatest: function() {
            return latest;
        },
    };
})();
