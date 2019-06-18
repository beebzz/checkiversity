
$.fn.makeItRain = function(){

  $(this).on('click',function(){

    var maxBills = 100;


    for (var i = 0; i < maxBills; i++){

    var random = $(window).width();

    var randomPosition = Math.floor(random*Math.random());

    var randomTime = Math.random() * 20;
    var randomSpeed = (Math.random()*20)+10 ;


    var bills = $("<span class='billsBillsBills'>")
      .css({
        left : randomPosition,
        top: '-150px',
        "-webkit-animation-delay" : randomTime + "s",
        "-webkit-animation-duration" : randomSpeed + "s"
      });

      $(bills).prepend('<img src="/resources/bill.svg" alt="a dollar bill">');


      $('body').append(bills);

    }; // end click function

  }); //end for loop

}; //end make it rain fn.


// Runs the function so that money rain when you click on the makeItRain Button //
$('#Rain_button').makeItRain();
