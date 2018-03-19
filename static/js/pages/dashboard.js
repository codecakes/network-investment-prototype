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

  jQuery("#dashboard_withdrawal").click(function() {
    $.ajax({
        type: "POST",
        url: "/send/",
        data: "",
        success: function(data) {
            if (data.status == "error") {
                toastr.warning(data.message, "Error", toastr_options);
            } else {
              jQuery("#dashboard_withdrawal_otp_modal").modal('show');
              $("#dashboard_withdrawal_otp").val();    
            }
        }
    });
  });

  jQuery("#dashboard_withdrawal_otp_send").click(function() {
    $.ajax({
        type: "POST",
        url: "/varify/",
        data: {
          "type":"withdraw",
          "otp": $("#dashboard_withdrawal_otp").val() 
        },
        success: function(data) {
            if (data.status == "error") {
                toastr.warning(data.message, "Error", toastr_options);
            } else {
              jQuery("#dashboard_withdrawal_otp_modal").modal('hide');
              toastr.success(data.message, "Success", toastr_options);
            }
        }
    });
  });

  $("input,select,textarea")
      .not("[type=submit]")
        .jqBootstrapValidation({
            submitError: function(){
              console.log("errooorr")
            },
            submitSuccess: function($form, event) {
                var formId = $form.attr("id");
                var data = getFormData($form);
                console.log("data ---",data)
                // $.ajax({
                //   type: "POST",
                //   url: "/withdraw",
                //   data: data,
                //   success: function(data) {
                //     data = JSON.parse(data);
                //     if (data.status == "error") {
                //       toastr.warning(data.message, "Error", toastr_options);
                //     } else {
                //       toastr.success(data.message, "Success", toastr_options);
                //     }
                //   }
                // });
            }
  });
});
