var DaysUI = (function() {
    var formatter = null;
    var palette = null;
    var $days = null;
    var $chart = null;
    var $help = null;
    var chart = null;
    var days = null;

    var init = function() {
        $chart.empty().hide();
        $days.find('.loading').show();
        $help.hide();
        chart = null;
        days = {};
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
                    if (this.point.color === undefined) {
                        return false;
                    }

                    return sprintf(
                        "<strong>Date</strong>: %s <strong>Amount</strong>: %s",
                        formatter.date(this.point.date),
                        formatter.amount(this.point.y, this.point.currency));
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
        var acc = 0.0;
        return function(day) {
            return {
                y: acc += day[chosenAmount],
                color: palette[chosenAmount](),
                date: day.date,
                currency: day.currency
            };
        };
    };

    var prepareNet = function(points) {
        var income = points[0];
        var outcome = points[1];

        return {
            y: (points[0].y + points[1].y),
            color: palette.net(),
            date: points[0].date,
            currency: points[0].currency
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

        initChart(income, outcome, net, categories); // Call this when the container is *visible*!
    };

    var updateDay = function(obj) {
        days[obj.date] = obj;
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

            if ($loading.is(':visible')) {
                $loading.hide();
            }

            _.map(data.stats.days, updateDay);

            if (_.any(_.filter(days, WithIncomeOrOutcomeNotNulls)) === false) {
                $chart.hide();
                $help.show();
            } else {
                $help.hide();
                $chart.show();
                updateChart();
            }
        },
    };
}());
