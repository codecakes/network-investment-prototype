$(function() {
  var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
      sURLVariables = sPageURL.split("&"),
      sParameterName,
      i;

    for (i = 0; i < sURLVariables.length; i++) {
      sParameterName = sURLVariables[i].split("=");

      if (sParameterName[0] === sParam) {
        return sParameterName[1] === undefined ? true : sParameterName[1];
      }
    }
  };

  function getFormData($form) {
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i) {
      indexed_array[n["name"]] = n["value"];
    });

    return indexed_array;
  };

	$("#placement_position").change(function() {
		if($(this).val() == 'R') {
			$("#placement_id_right").css("display", "block")
			$("#placement_id_left").css("display", "none")
		} else {
			$("#placement_id_right").css("display", "none")
			$("#placement_id_left").css("display", "block")
		}
	})

	$("#signup_password, #confirm_password").change(function() {
    if ($("#signup_password").val() && $("#confirm_password").val()) {
      if ($("#signup_password").val() == $("#confirm_password").val()) {
        $("#rePassword-matching-message")
          .html("Matching")
          .css("color", "green");
      } else {
        $("#signup_password-matching-message").html("");
        $("#rePassword-matching-message")
          .html("Not Matching")
          .css("color", "red");
      }
    } else {
      if ($("#signup_password").val() == "") {
        $("#signup_password-matching-message")
          .html("Required Field")
          .css("color", "red");
      } else {
        $("#signup_password-matching-message").html("");
      }

      if ($("#confirm_password").val() == "") {
        $("#rePassword-matching-message")
          .html("Required Field")
          .css("color", "red");
      } else {
        $("#rePassword-matching-message").html("");
      }
    }
  });

  $("#email").on("change", function() {
    if ($("#email").val()) {
      if (
        /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($("#email").val())
      ) {
        $("#email-matching-message")
          .html("Valid")
          .css("color", "green");
      } else {
        $("#email-matching-message")
          .html("Invalid email")
          .css("color", "red");
      }
    } else {
      $("#email-matching-message")
        .html("Required Field")
        .css("color", "red");
    }
  });

  $("#first_name").on("change", function() {
    if ($("#first_name").val()) {
      if (/^[a-zA-Z0-9 ]{2,30}$/.test($("#first_name").val())) {
        $("#first_name-matching-message")
          .html("Valid")
          .css("color", "green");
      } else {
        $("#first_name-matching-message")
          .html("Invalid name.use only character,digits and name only")
          .css("color", "red");
      }
    } else {
      $("#first_name-matching-message")
        .html("Required Field")
        .css("color", "red");
    }
  });

  $("#last_name").on("change", function() {
    if ($("#last_name").val()) {
      if (/^[a-zA-Z0-9 ]{2,30}$/.test($("#last_name").val())) {
        $("#last_name-matching-message")
          .html("Valid")
          .css("color", "green");
      } else {
        $("#last_name-matching-message")
          .html("Invalid name.use only character,digits and name only")
          .css("color", "red");
      }
    } else {
      $("#last_name-matching-message")
        .html("Required Field")
        .css("color", "red");
    }
  });

  $("#mobile").on("change", function() {
    if ($("#mobile").val()) {
      if (/^[0]?[789]\d{9}$/.test($("#mobile").val())) {
        $("#mobile-matching-message")
          .html("Valid")
          .css("color", "green");
      } else {
        $("#mobile-matching-message")
          .html(
            "Invalid mobile.Provide 10 digit valid mobile number start with 7,8 or 9"
          )
          .css("color", "red");
      }
    } else {
      $("#mobile-matching-message")
        .html("Required Field")
        .css("color", "red");
    }
  });

  var passwordValidation = function() {
    if ($("#signup_password").val() && $("#confirm_password").val()) {
      if ($("#signup_password").val() == $("#confirm_password").val()) {
        $("#rePassword-matching-message")
          .html("Matching")
          .css("color", "green");
        return true;
      } else {
        $("#signup_password-matching-message").html("");
        $("#rePassword-matching-message")
          .html("Not Matching")
          .css("color", "red");
        return false;
      }
    } else {
      var result = false;
      if ($("#signup_password").val() == "") {
        $("#signup_password-matching-message")
          .html("Required Field")
          .css("color", "red");
        result = false;
      } else if ($("#confirm_password").val() == "") {
        $("#rePassword-matching-message")
          .html("Required Field")
          .css("color", "red");
        result = false;
      } else {
        $("#rePassword-matching-message").html("");
        $("#signup_password-matching-message").html("");
        result = true;
      }
      return result;
    }
  };

  var emailValidation = function() {
    if ($("#email").val()) {
      if (
        /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($("#email").val())
      ) {
        $("#email-matching-message")
          .html("Valid")
          .css("color", "green");
        return true;
      } else {
        $("#email-matching-message")
          .html("Invalid email")
          .css("color", "red");
        return false;
      }
    } else {
      $("#email-matching-message")
        .html("Required Field")
        .css("color", "red");
      return false;
    }
  };

  var firstNameValidation = function() {
    if ($("#first_name").val()) {
      if (/^[a-zA-Z0-9 ]{2,30}$/.test($("#first_name").val())) {
        $("#first_name-matching-message")
          .html("Valid")
          .css("color", "green");
        return true;
      } else {
        $("#first_name-matching-message")
          .html("Invalid name.use only character,digits and name only")
          .css("color", "red");
        return false;
      }
    } else {
      $("#first_name-matching-message")
        .html("Required Field")
        .css("color", "red");
      return false;
    }
  };

  var lastNameValidation = function() {
    if ($("#last_name").val()) {
      if (/^[a-zA-Z0-9 ]{2,30}$/.test($("#last_name").val())) {
        $("#last_name-matching-message")
          .html("Valid")
          .css("color", "green");
        return true;
      } else {
        $("#last_name-matching-message")
          .html("Invalid name.use only character,digits and name only")
          .css("color", "red");
        return false;
      }
    } else {
      $("#last_name-matching-message")
        .html("Required Field")
        .css("color", "red");
      return false;
    }
  };

  var mobileValidation = function() {
    if ($("#mobile").val()) {
      if (/^[0]?[789]\d{9}$/.test($("#mobile").val())) {
        $("#mobile-matching-message")
          .html("Valid")
          .css("color", "green");
        return true;
      } else {
        $("#mobile-matching-message")
          .html(
            "Invalid mobile.Provide 10 digit valid mobile number start with 7,8 or 9"
          )
          .css("color", "red");
        return false;
      }
    } else {
      $("#mobile-matching-message")
        .html("Required Field")
        .css("color", "red");
      return false;
    }
  };

  $("#submit_mover").click(function(evt) {
    var emailResult = emailValidation();
    var firstNameResult = firstNameValidation();
    var lastNameResult = lastNameValidation();
    var mobileResult = mobileValidation();
    var passwordResult = passwordValidation();
    var form = $("#ragistrationFormMover");
    var data = getFormData(form);
    if (emailResult && firstNameResult && lastNameResult && passwordResult && mobileResult) {
      $("#pageLoader, #loader").show()
      $.ajax({
        type: "POST",
        url: "/signup/",
        data: data,
        success: function(prod_detail) {
          $("#pageLoader, #loader").hide()
          setTimeout(function() {
            var data = prod_detail;
            alert(data);
            window.location.reload();
          }, 500)
        }
      });
    }
  });
});
