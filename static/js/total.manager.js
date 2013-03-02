var TotalManager = (function() {
    var formatter = null;
    var $total = null;
    var total = null;

    var init = function() {
        $total.html("&nbsp");
        total = 0.0;
    };

    var update = function(amount) {
        total = amount;

        $total.text(sprintf("%s", formatter.amount(total, currency)));
    };

    return {
        onReady: function(formatter_, $total_, currency_) {
            formatter = formatter_;
            $total = $total_;
            currency = currency_;

            init();
        },


        onMonthChange: function(year, month) {
            init();
        },

        onAddAmount: function(amount) {
            if (amount > 0) {
                update(total + amount);
            }
        },

        onRemAmount: function(amount) {
            if (amount > 0) {
                update(total - amount);
            }
        }

    };
}());
