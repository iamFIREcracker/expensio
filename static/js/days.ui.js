var DaysUI = (function() {
    var __help = 'As soon as you start adding expenses, this space will be replaced ' 
               + 'with a chart showing how much you have spent, on a day by day basis, ' 
               + 'in the last 30 days';
    var __animationtimeout = 200; // milliseconds
    var __daysnumber = 30;

    var formatter = null;
    var palette = null;
    var $days = null;
    var chart = null;
    var days = null;
    var latest = null;
    var first = null;

    var init = function() {
        $days.html('<div class="loading"><img src="/static/images/loading.gif" /></div>')
        chart = null;
        days = Object();
        latest = '';
        first = true;

        for (var i = 0; i < __daysnumber; i++) {
            days[i] = null;
        }
    };

    var initChart = function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $days[0].id,
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
                        fontSize: '10px',
                    },
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
        /*
         * Chart lazy initialization.
         */
        if (chart == null) {
            initChart();
        }

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

    var showHelp = function() {
        $days.hide();
        $days.html('<div><p class="help">' + __help + '</p></div>');
        $days.fadeIn(__animationtimeout);
    }

    return {
        onReady: function(formatter_, palette_, $days_) {
            formatter = formatter_;
            palette = palette_;
            $days = $days_;

            init();
        },

        onNewData: function(data) {
            var hidehelp = false;

            $.each(data.days, EachCallbackWrapper(function(i, value, _this) {
                hidehelp = hidehelp || updateDay(value);
            }, this));

            if (hidehelp) {
                updateChart();
            } else if (first) {
                showHelp();
            }

            first = false;
        },


        getN: function() {
            return __daysnumber;
        },

        getLatest: function() {
            return latest;
        },
    };
})();
