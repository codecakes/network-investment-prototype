$(function(){
    function getFormData($form){
        var unindexed_array = $form.serializeArray();
        var indexed_array = {};

        $.map(unindexed_array, function(n, i){
            indexed_array[n['name']] = n['value'];
        });

        return indexed_array;
    }

    var treeDom = $("#networkTree");
    var addUserDom = $("#addUser-summary");
    if(addUserDom.length){
        $('#addUserButton').click(function(){
            $("#addUserContainer").slideToggle();
        });
    }
    $("#newUserAdd").click(function(){
        var newUserForm = $("#addUserForm");
        var newUserData = getFormData(newUserForm);
        // $.ajax({
        //      type: "POST",
        //      url: "",
        //      data: newUserData,
        //      success: function(result) {
        //          var data = result;
        //          window.location.reload();
        //      }
        //  });
    })

    if(treeDom.length){
        $.ajax({
            type: "POST",
            url: "/network",
            success: function(result) {
                var data = result
                console.log("-------",data)
                var networkData = chart_config = {
                    chart: {
                        container: "#networkTree",
                        
                        connectors: {
                            type: 'step'
                        },
                        node: {
                            HTMLclass: 'nodeExample1'
                        }
                    },
                    nodeStructure:JSON.parse(data)
                } 
                var networkTree = new Treant( chart_config );
            }
        });
    }
})