
function askPerson(a, b) {
    var resp = $.ajax({
        type: 'POST',
        url: '/puzzle/oh-the-places-youll-go/dynamic',
        data: {
            action: 'ask',
            arg1: a,
            arg2: b
        },
        dataType: 'json',
        async:false
    });
    return resp.responseJSON.reply
}
function tellPerson(a, b) {
    var resp = $.ajax({
        type: 'POST',
        url: '/puzzle/oh-the-places-youll-go/dynamic',
        data: {
            action: 'tell',
            arg1: a,
            arg2: b
        },
        dataType: 'json',
        async:false
    });
    return resp.responseJSON.reply
}
var success = 1;
function giveThing(a, b) {
    var resp = $.ajax({
        type: 'POST',
        url: '/puzzle/oh-the-places-youll-go/dynamic',
        data: {
            action: 'give',
            arg1: a,
            arg2: b
        },
        dataType: 'json',
        async:false
    });
    return resp.responseJSON.reply
}