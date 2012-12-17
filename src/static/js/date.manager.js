var DateManager = (function() {
    var __months = [ "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December" ];

    var $title = null;
    var curyear = null;
    var curmonth = null;

    var _init = function() {
        $title.text(sprintf("%s %d", __months[curmonth], curyear));
    };

    return {
        onReady: function($title_) {
            var date = new Date();

            $title = $title_;
            curyear = date.getYear() + 1900; // Fix relative to 1900
            curmonth = date.getMonth(); // 0-indexed months

            _init();
        },

        onMonthChange: function(year, month) {
            curyear = year;
            curmonth = month;

            _init();
        },


        getSince: function() {
            return sprintf('%d-%d-01', curyear, curmonth + 1)
        },

        getTo: function() {
            var lastofmonth = new Date(curyear, curmonth + 1, 0);
            return sprintf(
                    "%d-%d-%d", curyear, curmonth + 1, lastofmonth.getDate());
        },
    };

})();
