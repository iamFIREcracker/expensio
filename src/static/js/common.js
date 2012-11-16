function AjaxCallbackWrapper(func, udata) {
    return function(data) {
        func(data, udata);
    };
}

function EachCallbackWrapper(func, data) {
    return function(i, value) {
        func(i, value, data);
    }
}

function size(obj) {
    var size = 0, key;

    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }

    return size;
}
