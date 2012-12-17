var Formatter = (function() {

    return {
        amount: function(amount, currency) {
            return sprintf("%.2f %s", amount, currency);
        },

        date: function(date) {
            return date.split(' ')[0]; // XXX format date properly
        }
    }

})();
