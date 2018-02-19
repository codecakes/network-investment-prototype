jQuery(document).ready(function() {
  jQuery(".withdraw-currency").click(function() {
    if ($(this).data('value')) {
      $.ajax({
        type: "POST",
        url: "/withdraw",
        data: {
          currency: $(this).data('value')
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
