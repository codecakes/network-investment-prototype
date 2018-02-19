(function ($) {
	"use strict"; // Start of use strict

	// Vide - Video Background Settings
	$('body').vide({
		mp4: bankMp4,
		poster: bankPoster
		// mp4: "static/mp4/bg02.mp4",
		// poster: "static/img/bg-mobile-fallback.jpg"
	}, {
			posterType: 'jpg'
		});

	$("#form-Toggle").click(function () {
		$("input").val("")
		$(".social-icons").toggleClass('show')
	})

	$("#close-form-button").click(function () {
		$(".social-icons").removeClass('show');
	})

})(jQuery);
