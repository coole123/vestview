$(function() {

    var compnayData = {};
    var companies = [];
    data.forEach(function(obj){
        compnayData[obj.company] = [obj.price, obj.ticker, obj.change];
        companies.push(obj.company);
    });

    function buildDropdownItem(company, price, change){
        if(change < 0){
            var pct = '<img src="/static/imgs/down.png"></img>';
            var span = '<span>$ ' + price + '  ' + pct + ' (' + change + ')</span>'
        }
        else{
            var pct = '<img src="/static/imgs/up.svg"></img>';
             var span = '<span>$ ' + price + '  ' + pct + ' (+' + change + ')</span>'
        }
        return '<p class="split-para"><strong>' + company + span + '</strong></p>';
    }

    function split( val ) {
      return val.split( /,\s*/ );
    }

    function extractLast( term ) {
      return split( term ).pop();
    }

    $.ui.autocomplete.filter = function (array, term) {
        var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
        return $.grep(array, function (value) {
            return matcher.test(value.label || value.value || value);
        });
    };

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
                var html = buildDropdownItem(item.value, compnayData[item.value][0],
                                         compnayData[item.value][2])
                return $("<li class='dropdown-item'></li>")
                    .append(html)
                    .appendTo(ul);
            }
        }
    });

    $("#stock-search-btn").on("click", function(e){
        // get companies from search field, and convert to tickers
        var companies = split($('.autocomplete').val());
        companies.pop();
        var tickers = [];
        companies.forEach(function(company){
            tickers.push(compnayData[company][1]);
        })
        window.location = 'http://localhost:5000' + '/chart/' + tickers.join("&");
    })

    $('#stock-search-form').keypress(function(e){
        if(e.which === 13){//enter key pressed
            $('#stock-search-btn').click();
            return false;
        }
    });
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
