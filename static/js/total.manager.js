var TotalManager = (function() {
    var formatter = null;
    var $total = null;
    var outcome = null;
    var income = null;
    var currency = null;

    var init = function() {
        outcome = 0.0;
        income = 0.0;

        update(outcome, income);
    };

    var update = function(outcome_, income_) {
        outcome = outcome_;
        income = income_;

        $total.find('.income').text(income !== 0 ? formatter.amount(income) : '-');
        $total.find('.outcome').text(outcome !== 0 ? '+' + formatter.amount(outcome) : '-');
        $total.find('.currency').text(currency);
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
