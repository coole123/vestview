$(function() {
    $(".autocomplete").autocomplete({
        source: data,
        create: function() {
            $(this).data('ui-autocomplete')._renderItem  = function (ul, item) {
                return $("<li class='ui-menu-item'></li>")
                    .append('<a>' + item.label + " " + item.price + '</a>')
                    .appendTo(ul);
            }
        }
    });

    $("#stock-search-btn").on("click", function(e){
        var ticker = $('.autocomplete').val().toUpperCase();
        window.location.href = '/chart/' + ticker
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
