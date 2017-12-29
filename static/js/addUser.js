$(function(){
    function getFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });

        return indexed_array;
    }

    var addUserDom = $("#addNetworkUser-summary");
    if(addUserDom.length){
        $("#newNetworkUserAdd").click(function(){
            var newUserForm = $("#addNetworkUserForm");
            var newUserData = getFormData(newUserForm);
            console.log(newUserData)
            $.ajax({
                 type: "POST",
                 url: "",
                 data: newUserData,
                 success: function(result) {
                     var data = result;
                     window.location.reload();
                 }
             });
        })
    }
})