var ParamsManager = function(date, ui, mode, optionaldays) {
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
            since: date.ndaysback(optionaldays - 1),
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
