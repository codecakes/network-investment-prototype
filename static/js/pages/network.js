$(function() {
  var treeDom = $("#networkTree");

  if (treeDom.length) {
    $.ajax({
      type: "POST",
      url: "/network",
      success: function(result) {
        var data = result;
        console.log("-------", data);
        var networkData = (chart_config = {
          chart: {
            container: "#networkTree",

            connectors: {
              type: "step"
            },
            node: {
              HTMLclass: "nodeExample1"
            }
          },
          nodeStructure: JSON.parse(data)
        });
        var networkTree = new Treant(chart_config);
      }
    });
  }
});
