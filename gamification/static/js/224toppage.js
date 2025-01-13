$(function () {
    $(window).on('load', function () {
        $(".loader").delay(1000).fadeOut(500, function () {
            $(this).css("display", "none");
        });
    
        setTimeout(function () {
            $(".main").addClass("show");
        }, 2000);
    });
});