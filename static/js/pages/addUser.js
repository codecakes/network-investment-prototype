$(document).ready(function() {
    function getFormData($form) {
      var unindexed_array = $form.serializeArray();
      var indexed_array = {};
  
      $.map(unindexed_array, function(n, i) {
        indexed_array[n["name"]] = n["value"];
      });
  
      return indexed_array;
    }
  
    function addUserFormAjax(event, data) {
      event.preventDefault();
      $.ajax({
        type: "POST",
        url: "",
        data: data,
        success: function(prod_detail) {
          setTimeout(function() {
            var data = prod_detail;
            toastr.success("Add User", data)
            // window.location.reload();
          }, 500);
        }
      });
    }
  
    $("input,select,textarea")
      .not("[type=submit]")
      .jqBootstrapValidation({
        submitSuccess: function($form, event) {
            var data = getFormData($form);
            addUserFormAjax(event, data);
        }
      });
  });
  