var ParamsManager = function(date, ui, mode, submode) {
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
        var since = (submode === 'life') ? date.epoch() :
                    (submode === 'year') ? date.ndaysback(365 - 1) :
                                           date.ndaysback(365 - 1);
        var to = date.today();

        return {since: since, to: to};
    };

    return {
        get: function() {
            return params[mode]();
        }
    };
};
