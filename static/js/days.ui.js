chart = null;
var DaysUI = (function() {
    var __animationtimeout = 200; // milliseconds

    var ndays = null;
    var formatter = null;
    var palette = null;
    var $days = null;
    var $chart = null;
    //var chart = null;
    var days = null;
    var latest = null;

    var init = function() {
        $chart.empty().hide();
        $days.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        chart = null;
        days = Object();
        latest = '';

        _.map(_.range(ndays), function(i) { days[i] = null; });
    };

    var initChart = function(data, categories) {
        var fontFamily = $('body').css('fontFamily');
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $chart[0].id,
                type: 'column',
                animation: false,
            },
            title: {
                text: null,
            },
            subtitle: {
                text: null,
            },
            xAxis: {
                categories: categories,
                title: {
                    text: null
                },
                labels: {
                    rotation: -45,
                    align: 'right',
                    style: {
                        fontFamily: fontFamily,
                    },
                },
            },
            yAxis: {
                min: 0,
                title: {
                    text: null,
                },
                labels: {
                    overflow: 'justify',
                }
            },
            tooltip: {
                formatter: function() {
                    if (!this.y)
                        return false;

                    var d = this.point.obj;
                    return sprintf(
                        "Amount: %s", formatter.amount(d.amount, d.currency))
                },
                style: {
                    fontFamily: fontFamily,
                },
            },
            plotOptions: {
                bar: {
                    dataLabels: {
                        enabled: false
                    }
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
                data: data,
            }],
        });
    };

    var preparePoint = function(day) {
        if (day === null) {
            return 0.0;
        }

        return {
            y: day.amount,
            color: palette.chart(),
            obj: day
        };
    };

    var prepareLabel = function(day) {
        if (day === null) {
            return "";
        }

        return formatter.date(day.date);
    };

    var updatePoint = function(indexPointArray) {
        var i = indexPointArray[0];
        var point = indexPointArray[1];

        chart.series[0].data[i].update(point);
    };

    var updateChart = function() {
        var data = _.map(days, preparePoint);
        var categories = _.map(days, prepareLabel);

        // Lazy initialization
        if (chart == null) {
            initChart(data, categories); // Call this when the container is *visible*!
        } else {
            _.map(_.zip(_.range(data.length), data), updatePoint);
            chart.xAxis[0].setCategories(categories);
        }

    }

    var updateDay = function(obj) {
        var i = obj.delta + ndays - 1;
        var prev = days[i];

        /*
         * Update the variable containing the date of the latest update.
         * This operation should be done on all received updates, even those
         * representing deleted items.
         */
        if (obj.updated > latest) {
            latest = obj.updated;
        }

        /*
         * The current day has no expenses (amount equal 0.0).  Check
         * for a previously received update: if present, issue a graceful
         * remove, otherwise return.
         */
        if (obj.amount == 0.0) {
            if (prev === null) {
                return false;
            } else {
                days[i] = null;
                return true;
            }
        }

        days[i] = obj;
        return true;
    };

    return {
        onReady: function(ndays_, formatter_, palette_, $days_) {
            ndays = ndays_;
            formatter = formatter_;
            palette = palette_;
            $days = $days_;
            $chart = $days.find('#days-chart');
            $help = $days.find('.alert');

            init();
        },

        onNewData: function(data) {
            var $loading = $days.find('.loading');

            if ($loading.length) {
                $loading.remove();
            }

            _.map(data.stats.days, updateDay);

            if (_.any(days) == false) {
                $chart.hide();
                $help.show();
            } else {
                $help.hide();
                $chart.show();
                updateChart();
            }
        },


        getN: function() {
            return ndays;
        },

        getLatest: function() {
            return latest;
        },
    };
})();
