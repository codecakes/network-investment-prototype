$(function() {
  function getFormData($form) {
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i) {
      indexed_array[n["name"]] = n["value"];
    });

    return indexed_array;
  }

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

  $("#newNetworkUserAdd").click(function(evt) {
    var emailResult = emailValidation();
    var firstNameResult = firstNameValidation();
    var lastNameResult = lastNameValidation();
    var mobileResult = mobileValidation();
    var form = $("#addNetworkUserForm");
    var data = getFormData(form);
    if (emailResult && firstNameResult && lastNameResult && mobileResult) {
      $("#pageLoader, #loader").show();
      $.ajax({
        type: "POST",
        url: "",
        data: data,
        success: function(prod_detail) {
          $("#pageLoader, #loader").hide();
          setTimeout(function() {
            var data = prod_detail;
            alert(data);
            window.location.reload();
          }, 500);
        }
      });
    }
  });
});
