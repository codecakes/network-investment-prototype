$(document).ready(function() {
	function getFormData($form) {
		var unindexed_array = $form.serializeArray();
		var indexed_array = {};

		$.map(unindexed_array, function(n, i) {
			indexed_array[n["name"]] = n["value"];
		});

		return indexed_array;
	}

	$("#country").change(function() {
		var optionSelected = $("option:selected", this);
		$("#countryCode").html(optionSelected.data("code"));
	})

	function addUserFormAjax(event, data) {
		var block_element = $(event.target).closest(".card");
		block_element.block(block_options)
		event.preventDefault();
		$.ajax({
			type: "POST",
			url: "",
			data: data,
			success: function(data) {
				block_element.unblock()
				data = JSON.parse(data)
				if(data.status == "error") {
					toastr.warning(data.message, "Error", toastr_options);
				} else {
					toastr.success(data.message, "Success", toastr_options);
				}
			}
		});
	}
	
	$("#country").change(function() {
		var optionSelected = $("option:selected", this);
		$("#countryCode").html(optionSelected.data("code"));
	})
	
	$("input,select,textarea")
		.not("[type=submit]")
		.jqBootstrapValidation({
			submitSuccess: function($form, event) {
				var data = getFormData($form);
				addUserFormAjax(event, data);
			}
		});
});
