var PeriodParamsManager = function(date, ui) {
    return {
        get: function() {
            var data = {
                since: date.startofcurrentmonth(),
                to: date.endofcurrentmonth(),
            };
            var latest = ui.getLatest();

            if (latest) {
                data.latest = latest;
            }

            return data;
        }
    };
};

var DaysParamsManager = function(date, mode, submode) {
    return {
        get: function() {
            var since;

            if (submode === 'life') {
                since = date.epoch();
            } else if (submode === 'year') {
                since = date.ndaysback(365 - 1);
            } else if (submode === 'quadrimester') {
                since = date.ndaysback(120 - 1);
            }

            return {since: since, to: date.today()};
        }
    };
}
