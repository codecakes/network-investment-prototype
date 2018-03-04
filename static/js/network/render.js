"use strict";

//Steps:
//1. Implement /network/init/user_id that returns traverse_tree(user) response
//2. On expanding any node, AJAX fires off GET '/network/children/58'
//   Implement this api on the backend return the value of 'children' key like
//{'children': children} and the tree will automagically render the child nodes here

// clicking a node with id=58 automatically calls GET:'/network/children/58'

$(function() {
  var loaded = false
  var nodeTemplate = function(data) {
    if(data.id) {
      return `
        <span>${data.avi_id}</span>
        <div class="title">${data.name}</div>
        <div class="content">
        <p class="m-0">Package: ${data.package}</p>
        <p class="m-0">Invest: ${data.investment}</p>
        <p class="m-0">Trans.: ${data.transaction}</p>
        </div>
      `;
    } else {
      return ` 
      <div class="title">${data.name}</div>
    `;
    }
  };
  let ajaxURL = {
      children: "/network/children/",
      parent: "/network/parent/",
      siblings: node => {
        return `/network/siblings/${node.id}`;
      },
      families: node => {
        return `/network/families/${node.id}`;
      }
    },

    // renderTree = function(treeData) {
    //   // TODO: id = getCurrentUserId - implement a function that takes the logged in users user.id
    //   // then use that here like `/network/init/${id}`
    //   let oc = $("#chart-container").orgchart({
    //     data: '/network/children/81',
    //     //ajaxURL: ajaxURL,
    //     //visibleLevel:4,
    //     'collapsed': false,
    //     zoom: false,  
    //     pan: false,
    //     toggleSiblingsResp: false,
    //     nodeTemplate: nodeTemplate
    //   });
    // };
    // renderTree(orgData);

    initOrgchart = function(nodeId, chartClass) {
      var url="";
      if(loaded == true) {
        url = '/network/children/'+nodeId;
      } else {
        url = '/network/init';
        loaded=true;      
      }
        $('#chart-container').orgchart({
          'data' : url,
          visibleLevel:4,
          'collapsed': false,
          zoom: false,
          depth:4,
          chartClass:chartClass||"root",  
          pan: false,
          toggleSiblingsResp: false,
          nodeTemplate: nodeTemplate,
          'createNode': function($node, data) {
            if(!data.has_pkg){
              $($node).find(".title").addClass("inactive-node-title")
              $($node).find(".content").addClass("inactive-node-border")
              $($node).addClass('inactive-node')
            }

            if(!data.avi_id){
              $($node).find(".title").addClass("nouser-node-title")
              $($node).find(".content").addClass("nouser-node-border")
              $($node).addClass('nouser-node')
            }

            if(data.avi_id && data.className && data.className.match(/top-level/)) {
            } else if(data.className && data.className.match(/drill-up/)) {
                  $($node).addClass(data.avi_id)             
                //var assoClass = data.className.match(/asso-\w+/)[0];
                var drillUpIcon = $('<i>', {
                  'class': 'fa fa-arrow-circle-up drill-icon',
                  'click': function() {
                    $('#chart-container').find('.orgchart:visible').addClass('hidden')
                    $($('.top-level').closest(".orgchart")).removeClass("hidden");
                    //$('#chart-container').find('.drill-down.' + data.avi_id).closest('.orgchart').removeClass('hidden');    
                    // $('#chart-container').find('.drill-down').closest('.orgchart').removeClass('hidden');
                    // $($("[id='"+data.id+"'][class='node drill-up']").closest(".orgchart")[0]).addClass("hidden")
                  }
                });
                $node.append(drillUpIcon);
            } else  if(data.avi_id){
                $($node).addClass('drill-down');
                $($node).addClass(data.avi_id)
                //var assoClass = data.className.match(/asso-\w+/)[0];
                var drillDownIcon = $('<i>', {
                  'class': 'fa fa-arrow-circle-down drill-icon',
                  'click': function() {
                    $('#chart-container').find('.orgchart:visible').addClass('hidden');
                    initOrgchart(data.id)
                    // if (!$('#chart-container').find('.orgchart.' + assoClass).length) {
                    //   initOrgchart(assoClass);
                    // } else {
                    //   $('#chart-container').find('.orgchart.' + assoClass).removeClass('hidden');
                    // }
                  }
                });
                $node.append(drillDownIcon);
              }
            }
        });
      }

      initOrgchart(1)
});
