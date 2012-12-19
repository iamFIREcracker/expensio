var DateManager = (function() {
    var __months = [ "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December" ];

    var $title = null;
    var today = null;
    var curyear = null;
    var curmonth = null;

    var _init = function() {
        $title.text(sprintf("%s %d", __months[curmonth], curyear));
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
        onReady: function($title_) {
            var date = new Date();

            $title = $title_;
            today = date;
            curyear = year(date);
            curmonth = month(date); // 0-indexed months

            _init();
        },

        onMonthChange: function(year, month) {
            curyear = year;
            curmonth = month;

            _init();
        },


        today: function() {
            return sprintf(
                    '%d-%d-%d', year(today), month(today) + 1, day(today));
        },

        getSince: function() {
            return sprintf('%d-%d-01', curyear, curmonth + 1)
        },

        getTo: function() {
            var lastofmonth = new Date(curyear, curmonth + 1, 0);

            return sprintf(
                    "%d-%d-%d", curyear, curmonth + 1, day(lastofmonth));
        },

        ndaysback: function(n) {
            var date = new Date(year(today), month(today), day(today) - n);

            return sprintf(
                    "%d-%d-%d", year(date), month(date) + 1, day(date));
        },
    };

})();
