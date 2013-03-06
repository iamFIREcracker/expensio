var DaysUI = (function() {
    var __animationtimeout = 200; // milliseconds

    var ndays = null;
    var formatter = null;
    var palette = null;
    var $days = null;
    var $chart = null;
    var $help = null;
    var chart = null;
    var days = null;
    var addamountlisteners = [];

    var init = function() {
        $chart.empty().hide();
        $days.append('<div class="loading"><img src="/static/images/loading.gif" /></div>');
        $help.hide();
        chart = null;
        days = {};

        _.map(_.range(ndays), function(i) { days[i] = null; });
    };

    var initChart = function(income, outcome, net, categories) {
        var fontFamily = $('body').css('fontFamily');
        chart = new Highcharts.Chart({
            chart: {
                renderTo: $chart[0].id,
                animation: false,
                type: 'area'
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
                title: {
                    text: null,
                },
                labels: {
                    overflow: 'justify',
                }
            },
            tooltip: {
                formatter: function() {
                    if (!this.y) {
                        return false;
                    }

                    var d = this.point.obj;
                    return sprintf(
                        "<strong>Date</strong>: %s <strong>Amount</strong>: %s",
                        formatter.date(d.date),
                        formatter.amount(this.point.y, d.currency));
                },
                style: {
                    fontFamily: fontFamily,
                },
            },
            plotOptions: {
                area: {
                    marker: {
                        enabled: false
                    }
                }
            },
            legend: {
                enabled: true,
            },
            credits: {
                enabled: false
            },
            series: [{
                name: 'Income',
                data: income,
                color: palette.income()
            },{
                name: 'Outcome',
                data: outcome,
                color: palette.outcome()
            },{
                name: 'Net',
                data: net,
                color: palette.net()
            }],
        });
    };

    var preparePoint = function(chosenAmount) {
        var cum = 0.0;
        return function(day) {
            return {
                y: cum += day[chosenAmount],
                color: palette[chosenAmount](),
                obj: day
            };
        };
    };

    var prepareNet = function(points) {
        var income = points[0];
        var outcome = points[1];

        return {
            y: (points[0].y + points[1].y),
            color: palette.net(),
            obj: points[0].obj
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
        var income = _.map(days, preparePoint('income'));
        var outcome = _.map(days, preparePoint('outcome'));
        var net = _.map(_.zip(income, outcome), prepareNet);
        var categories = _.map(days, prepareLabel);

        // Lazy initialization
        if (chart === null) {
            initChart(income, outcome, net, categories); // Call this when the container is *visible*!
        } else {
            _.map(_.zip(_.range(data.length), data), updatePoint);
            chart.xAxis[0].setCategories(categories);
        }
    };

    var updateDay = function(obj) {
        var i = obj.delta + ndays - 1;
        var prev = days[i];

        /*
         * The current day has no expenses (amount equal 0.0).  Check
         * for a previously received update: if present, issue a graceful
         * remove, otherwise return.
         */
        if (obj.amount === 0.0) {
            if (prev === null) {
                return false;
            }

            days[i] = null;
            return true;
        }

        days[i] = obj;
        $.each(addamountlisteners, function(index, func) {
            func(obj.income);
            func(obj.outcome);
        });
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

            if (_.any(days) === false) {
                $chart.hide();
                $help.show();
            } else {
                $help.hide();
                $chart.show();
                updateChart();
            }
        },


        addAmount: function(func) {
            addamountlisteners.push(func);
        },

    };
}());
