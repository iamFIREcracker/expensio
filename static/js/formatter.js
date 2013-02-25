var Formatter = (function() {

    return {
        amount: function(amount, currency) {
            return sprintf("%.2f %s", amount, currency === null ? "" : currency);
        },

        date: function(datestring) {
            var date = new Date(datestring);
            var today = new Date();
            var sameyear = today.getYear() === date.getYear();
            var sameday = sameyear &&
                          today.getMonth() === date.getMonth() &&
                          today.getDate() === date.getDate();

            if (sameday) {
                return "Today";
            } else if (sameyear) {
                var items = date.toDateString().split(' ');
                var month = items[1];
                var day = date.getDate();

                return sprintf("%s %s", month, day);
            } else {
                var items = date.toDateString().split(' ');
                var day = items[2];
                var month = date.getMonth() + 1;
                var year = date.getYear() + 1900;

                return sprintf("%d/%s/%d", month, day, year);
            }
        },

        yearly: function(datestring) {
            return this.date(sprintf("%s/%d", datestring, new Date().getYear() + 1900));
        },

        monthly: function(monthly) {
            var msg;

            if (monthly === 1) {
                msg = "1st";
            } else if (monthly === 2) {
                msg = "2nd";
            } else if (monthly === 3) {
                msg = "3rd";
            } else {
                msg = sprintf("%dth", monthly);
            }

            return msg;
        },

        weekly: function(weekly) {
            if (!weekly) {
                return "";
            }

            return weekly;
        }
    };

}());
