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
            toastr.warning(data.message, "Error", toastr_options);
          } else {
            toastr.success(data.message, "Success", toastr_options);
          }
        }
      });
    } else {
      toastr.warning("Select currency for withdraw.", "Error", toastr_options);
    }
  });
});
