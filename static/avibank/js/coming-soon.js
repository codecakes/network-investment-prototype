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
		var data = { };
	
		$.each($('#bankSubscribeForm').serializeArray(), function() {
		    data[this.name] = this.value;
		});
		$.ajax({
			type: "POST",
			url: "/bank/",
			data: data,
			success: function(data) {
				data = JSON.parse(data)
				if(data.status == "error") {
				toastr.warning(data.message, "Error");
				} else {
				toastr.success(data.message, "Success");
				}
			}
		  });
		// $.ajax({
		//         type: "POST",
		//         url: "/bank/",
		//         data: result,
		//         contentType: "application/json"
		//     })
	})

})(jQuery);
