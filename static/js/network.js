$(function(){
    $.ajax({
        type: "POST",
        url: "/network",
        success: function(prod_detail) {
            var data = prod_detail//JSON.parse(prod_detail)
            console.log(data,"fkgnkfng")
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
            new Treant( chart_config );
        }
    });
})