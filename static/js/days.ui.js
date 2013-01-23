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
        $chart.empty();
        $days.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        chart = null;
        days = Object();
        latest = '';

        for (var i = 0; i < __daysnumber; i++) {
            days[i] = null;
        }

        initChart();
        $chart.hide(); // It is important to hide the chart here!!!
    };

    var initChart = function() {
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
                },
            },
            yAxis: {
                min: 0,
                title: {
                    text: null,
                },
                labels: {
                    overflow: 'justify'
                }
            },
            tooltip: {
                formatter: function() {
                    if (!this.y)
                        return false;

                    var d = this.point.obj;
                    return sprintf(
                        "Amount: %s", formatter.amount(d.amount, d.currency))
                }
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

    var updateChart = function() {
        var daynames = Array();
        var dayamounts = Array();

        for (var i in days) {
            var d = days[i];

            if (d == null) {
                daynames.push("");
                dayamounts.push(0.0);
            } else {
                daynames.push(formatter.date(d.date));
                dayamounts.push({y: d.amount, color: palette.chart(), obj: d});
            }
        }

        chart.series[0].setData(dayamounts);
        chart.xAxis[0].setCategories(daynames);
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

            $.each(data.days, EachCallbackWrapper(function(i, value, _this) {
                updateDay(value);
            }, this));

            if (_.any(days) == false) {
                console.log("show-help");
                $chart.hide();
                $help.show();
            } else {
                console.log("show-chart");
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
