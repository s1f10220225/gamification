$(function () {
    $(window).on('load', function () {
        $(".loader").delay(1500).fadeOut(1000, function () {
            $(this).css("display", "none");
        });
    
        setTimeout(function () {
            $(".main").addClass("show");
        }, 2500);
    });
});