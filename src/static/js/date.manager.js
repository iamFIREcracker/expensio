var DateManager = (function() {
    var __months = [ "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December" ];

    var _$title = null;
    var _curyear = null;
    var _curmonth = null;

    var _init = function() {
        _$title.text(sprintf("%s %d", __months[_curmonth], _curyear));
    };

    return {
        onReady: function($title) {
            var date = new Date();

            _$title = $title;
            _curyear = date.getYear() + 1900; // Fix relative to 1900
            _curmonth = date.getMonth(); // 0-indexed months

            _init();
        },

        onMonthChange: function(year, month) {
            _curyear = year;
            _curmonth = month;

            _init();
        },


        getSince: function() {
            return sprintf('%d-%d-01', _curyear, _curmonth + 1)
        },

        getTo: function() {
            var lastofmonth = new Date(_curyear, _curmonth + 1, 0);
            return sprintf(
                    "%d-%d-%d", _curyear, _curmonth + 1, lastofmonth.getDate());
        },
    };

})();
