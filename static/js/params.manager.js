var ParamsManager = (function() {

    var mode = null;
    var date = null;
    var ui = null;

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
        onReady: function(mode_, date_, ui_) {
            mode = mode_;
            date = date_;
            ui = ui_;
        },

        get: function() {
            return params[mode]();
        }
    };
}());
