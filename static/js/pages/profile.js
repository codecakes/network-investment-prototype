$(document).ready(function() {
	$("a.scroll").click(function(event) {
		event.preventDefault();
		$("html, body").animate({
			scrollTop: $($(this).attr("href")).offset().top - 80
		});
	});

	$("input,select,textarea").not("[type=submit]").jqBootstrapValidation({});

	if($(".sidebar-sticky").length) {
		var headerNavbarHeight, footerNavbarHeight;
		$("body").hasClass("vertical-content-menu")
			? ((headerNavbarHeight = 0), (footerNavbarHeight = 0))
			: $("body").hasClass("content-right-sidebar") ||
				$("body").hasClass("content-left-sidebar")
				? ((headerNavbarHeight = $(".header-navbar").height()),
					(footerNavbarHeight = $("footer.footer").height()))
				: ((headerNavbarHeight = $(".header-navbar").height() + 24),
					(footerNavbarHeight = $("footer.footer").height() + 10)),
			$(".sidebar-sticky").sticky({
				topSpacing: headerNavbarHeight,
				bottomSpacing: footerNavbarHeight
			});
	}

	$("#profile_personal_detail_form").submit(function(event) {
		event.preventDefault();
		var block_element = $(event.target).closest(".card");
		block_element.block(block_options)
		var data = {
			action: "profile",
			first_name: $("#first_name").val(),
			last_name: $("#last_name").val(),
			country: $("#country").val()
		};

		$.ajax({
			type: "POST",
			url: "/profile",
			dataType: "json",
			data: data,
			success: function(data) {
				block_element.unblock()
				toastr.success(data.message, "Success", toastr_options);
			}
		});
	});

	$("#profile_crypto_accounts_form").submit(function(event) {
		event.preventDefault();

		if($("#xrp_address").val()) {
			if(!$("#xrp_destination_tag").val()) {
				$("#xrp_error").html("Ripple Destination tag required with Ripple address.")
				return false
			} else {
				$("#xrp_error").html("")
			}
		}
		
		var block_element = $(event.target).closest(".card");
		block_element.block(block_options)

		var data = {
			action: "crypto",
			btc_address: $("#btc_address").val(),
			eth_address: $("#eth_address").val(),
			xrp_address: $("#xrp_address").val(),
			xrp_destination_tag: $("#xrp_destination_tag").val(),
		};

		$.ajax({
			type: "POST",
			url: "/profile",
			dataType: "json",
			data: data,
			success: function(data) {
				console.log(data)
				block_element.unblock()
				toastr.success(data.message, "Success", toastr_options);
			}
		});
	});

	$("#profile_change_password_form").submit(function(event) {
		event.preventDefault();
		var block_element = $(event.target).closest(".card");
		block_element.block(block_options)
		var data = {
			action: "password",
			password: $("#password").val()
		};

		$.ajax({
			type: "POST",
			url: "/profile",
			dataType: "json",
			data: data,
			success: function(data) {
				block_element.unblock()
				toastr.success(data.message, "Success", toastr_options);
			}
		});
	});
});
