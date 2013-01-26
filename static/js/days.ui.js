var DaysUI = (function() {
    var __animationtimeout = 200; // milliseconds
    var __daysnumber = 30;

    var formatter = null;
    var palette = null;
    var $days = null;
    var $chart = null;
    var chart = null;
    var days = null;
    var latest = null;

    var init = function() {
        $chart.empty().hide();
        $days.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        chart = null;
        days = Object();
        latest = '';

        _.map(_.range(__daysnumber), function(i) { days[i] = null; });
    };

    var initChart = function() {
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
                data: [],
            }]
        });
    };

    var preparePoint = function(day) {
        if (day == null)
            return 0.0;
        else
            return {
                y: day.amount,
                color: palette.chart(),
                obj: day
            };
    }

    var prepareLabel = function(day) {
        if (day == null)
            return "";
        else
            return formatter.date(day.date);
    }

    var updateChart = function() {
        // Lazy initialization
        if (chart == null) {
            initChart(); // Call this when the container is *visible*!
        }

        chart.series[0].setData(_.map(days, preparePoint));
        chart.xAxis[0].setCategories(_.map(days, prepareLabel));
    }

    var updateDay = function(obj) {
        var i = obj.delta + __daysnumber - 1;
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
        onReady: function(formatter_, palette_, $days_) {
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

            _.map(data.days, updateDay);

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
            return __daysnumber;
        },

        getLatest: function() {
            return latest;
        },
    };
})();
