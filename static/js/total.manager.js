var TotalManager = (function() {
    var formatter = null;
    var $total = null;
    var outcome = null;
    var income = null;

    var init = function() {
        outcome = 0.0;
        income = 0.0;

        update(outcome, income);
    };

    var update = function(outcome_, income_) {
        outcome = outcome_;
        income = income_;

        $total.text(sprintf("%s", formatter.amount(outcome, currency)));
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
                update(outcome + amount, income);
            } else if (amount < 0) {
                update(outcome, income + amount);
            }
        },

        onRemAmount: function(amount) {
            if (amount > 0) {
                update(outcome - amount);
            } else if (amount < 0) {
                update(outcome, income - amount);
            }
        }

    };
}());
