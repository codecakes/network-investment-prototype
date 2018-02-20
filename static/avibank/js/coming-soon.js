(function ($) {
	"use strict"; // Start of use strict

	// Vide - Video Background Settings
	$('body').vide({
		mp4: bankMp4
		//poster: bankPoster
		// mp4: "static/mp4/bg02.mp4",
		// poster: "static/img/bg-mobile-fallback.jpg"
	});

	$("#form-Toggle").click(function () {
		$("input").val("")
		$(".social-icons").toggleClass('show')
	})

	$("#close-form-button").click(function () {
		$(".social-icons").removeClass('show');
	})

	$("#bankSubscribe").click(function(){
		let result = { };
		$.each($('#bankSubscribeForm').serializeArray(), function() {
		    result[this.name] = this.value;
		});
		console.log("result ==",result)
		$.ajax({
		        type: "POST",
		        url: "/bank",
		        data: result,
		        contentType: "application/json"
		    })
	})

})(jQuery);
