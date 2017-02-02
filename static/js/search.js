$(function() {

    var priceAndTicker = {};
    var companies = [];
    console.log(data);
    data.forEach(function(obj){
        priceAndTicker[obj.company] = [obj.price, obj.ticker];
        companies.push(obj.company);
    });

    function split( val ) {
      return val.split( /,\s*/ );
    }

    function extractLast( term ) {
      return split( term ).pop();
    }

    $(".autocomplete")
    // don't navigate away from the field on tab when selecting an item
    .on( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.TAB &&
            $( this ).autocomplete( "instance" ).menu.active ) {
          event.preventDefault();
        }
    })
    .autocomplete({
        source: function( request, response ) {
              // delegate back to autocomplete, but extract the last term
              response( $.ui.autocomplete.filter(
                companies, extractLast( request.term ) ) );
        },
        focus: function(){
            return false;
        },
        select: function(event, ui){
            var terms = split( this.value );
            // remove the current input
            terms.pop();
            // add the selected item
            terms.push( ui.item.value );
            // add placeholder to get the command and space at end
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
        },
        create: function() {
            $(this).data('ui-autocomplete')._renderItem  = function (ul, item) {
                return $("<li class='ui-menu-item'></li>")
                    .append('<a>' + item.value + "    " + priceAndTicker[item.value][0] + '</a>')
                    .appendTo(ul);
            }
        }
    });

    $("#stock-search-btn").on("click", function(e){
        // get companies from search field, and convert to tickers
        var companies = split($('.autocomplete').val()); companies.pop();
        var tickers = [];
        companies.forEach(function(company){
            tickers.push(priceAndTicker[company][1]);
        })
        window.location.href = '/chart/' + tickers.join("&");
    })
});

/*-----------------------------------------------------------------
   Updates timestamp every second on search page*/
var currTime = new Date();

function updateTimestamp() {
    /// Increment by one second
    currTime = new Date(currTime.getTime() + 1000);
    $('#timestamp').html(currTime.toGMTString());
}
// updates timestamp every second, bloat
$(function() {
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
});
/*-------------------------------------------------------------------*/
