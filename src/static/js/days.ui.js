var DaysUI = (function() {
    var __daysnumber = 30;

    var $days = null;
    var chart = null;
    var days = null;
    var latest = null;

    var init = function() {
        $days.empty();
        chart = null;
        days = Object();
        latest = '';

        for (var i = 0; i < __daysnumber; i++) {
            days[i] = null;
        }
    };

    var initChart = function() {
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $days[0].id,
                type: 'column',
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

        var daynames = Array();
        var dayamounts = Array();

        for (var i in days) {
            var d = days[i];

            if (d == null) {
                daynames.push("");
                dayamounts.push(0.0);
            } else {
                daynames.push(d.date);
                dayamounts.push(d.amount);
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
            if (prev === undefined) {
                return;
            } else {
                days[i] = null;
                return
            }
        }

        days[i] = obj;
    };

    return {
        onReady: function($days_) {
            $days = $days_;

            init();
        },

        onNewData: function(data) {
            if (data.days.length) {
                $.each(data.days, EachCallbackWrapper(function(i, value, _this) {
                    updateDay(value);
                }, this));

                updateChart();
            }
        },


        getLatest: function() {
            return latest;
        },
    };
})();
