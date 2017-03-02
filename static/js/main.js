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

  $(document).ready(function() {
    $('input#pass').characterCounter();
    $('.modal').modal();
  });

 