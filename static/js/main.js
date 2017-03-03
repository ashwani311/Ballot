var isEmpty = function( i ) {
    if((i=="")||(i==null)){
        return true;
    }
    if(/\S/.test( i )) {
        return true;
    }
    return false;
};

var isPhone = function( i ) {
    if ((/^\d{10}$/).test(i)) {
        if(i.length == 10) {
            return true;
        }
    }
    return false;
}

$(".button-collapse").sideNav();

$('.datepicker').pickadate({
    selectMonths: true, // Creates a dropdown to control month
    selectYears: 1, // Creates a dropdown of 15 years to control year
    formatSubmit: 'yyyy/mm/dd',
    hiddenName: true
});

$(document).ready(function() {
    $('input#pass').characterCounter();
    $('.modal').modal();
});
