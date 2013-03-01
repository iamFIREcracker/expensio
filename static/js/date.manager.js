var DateManager = (function() {
    var __months = [ "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December" ];

    var $title = null;
    var today = null;
    var curyear = null;
    var curmonth = null;

    var _init = function() {
        $title.text(sprintf("%s %d", __months[curmonth - 1], curyear));
    };

    var year = function(date) {
        return date.getYear() + 1900;
    };

    var month = function(date) {
        return date.getMonth();
    };

    var day = function(date) {
        return date.getDate();
    };

    return {
        onReady: function($title_, year, month) {
            var date = new Date();

            $title = $title_;
            today = date;
            curyear = year
            curmonth = month;

            _init();
        },

        onMonthChange: function(year, month) {
            curyear = year;
            curmonth = month;

            _init();
        },

        epoch: function() {
            return "1970-01-01";
        },

        today: function() {
            return sprintf(
                    '%d-%02d-%02d', year(today), month(today) + 1, day(today));
        },

        year: function() {
            return curyear;
        },

        month: function() {
            return curmonth;
        },

        period: function() {
            return sprintf(
                    '%d-%02d', year(today), month(today) + 1);
        },

        ndaysback: function(n) {
            var date = new Date(year(today), month(today), day(today) - n);

            return sprintf(
                    "%d-%02d-%02d", year(date), month(date) + 1, day(date));
        },

        startofcurrentmonth: function() {
            return sprintf('%d-%02d-01', curyear, curmonth)
        },

        endofcurrentmonth: function() {
            var lastofmonth = new Date(curyear, curmonth, 0);

            return sprintf(
                    "%d-%02d-%02d", curyear, curmonth, day(lastofmonth));
        },
    };

}());
