jQuery(document).ready(function() {
  jQuery("#withdrawButton").click(function() {
    if ($("#withdrawCurrency").val()) {
      $.ajax({
        type: "POST",
        url: "/withdraw",
        data: {
          currency: $("#withdrawCurrency").val()
        },
        headers: {
            "X-CSRFToken": $("[name='csrfmiddlewaretoken']").val()
        },
        success: function(data) {
          data = JSON.parse(data);
          if (data.status == "error") {
            toastr.warning(data.message, "Error");
          } else {
            toastr.success(data.message, "Success");
          }
        }
      });
    } else {
      toastr.warning("Select currency for withdraw.", "Error");
    }
  });
});
