var ParamsManager = function(mode, date, ui) {
    var params = {
        'period': function() { return period(); },
        'days': function() { return days(); },
    };

    var period = function() {
        var data = {
            since: date.startofcurrentmonth(),
            to: date.endofcurrentmonth(),
        };
        var latest = ui.getLatest();

        if (latest) {
            data.latest = latest;
        }

        return data;
    };

    var days = function() {
        var data = {
            since: date.ndaysback(ui.getN() - 1),
            to: date.today(),
        };
        var latest = ui.getLatest();

        if (latest) {
            data.latest = latest;
        }

        return data;
    };

    return {
        get: function() {
            return params[mode]();
        }
    };
};
