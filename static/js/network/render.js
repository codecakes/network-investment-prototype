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
      <span>No User</span>
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
    // var orgData = {
    //   "transaction": 0,
    //   "name": "Harshul kaushik",
    //   "relationship": "011",
    //   "package": 0,
    //   "image": "/static/images/node2.png",
    //   "placement_id": null,
    //   "id": 1,
    //   "investment": 0,
    //   "className": "top-level",
    //   "avi_id": "AVI000000001",
    //   "placement_position": null,
    //   "sponsor_id": null,
    //   "link": {
    //     "href": "https://www.avicrypto.us/network#"
    //   },
    //   "children": [
    //     {
    //       "transaction": 0,
    //       "name": "Robert John",
    //       "relationship": "111",
    //       "package": 5000,
    //       "image": "/static/images/node2.png",
    //       "placement_id": 1,
    //       "id": 57,
    //       "investment": 5000,
    //       "avi_id": "AVI000000019",
    //       "placement_position": "L",
    //       "sponsor_id": 1,
    //       "link": {
    //         "href": "https://www.avicrypto.us/network#"
    //       },
    //       "children": [
    //         {
    //           "transaction": 0,
    //           "name": "Erwin Yap",
    //           "relationship": "111",
    //           "package": 1000,
    //           "image": "/static/images/node2.png",
    //           "placement_id": 57,
    //           "id": 80,
    //           "investment": 1000,
    //           "avi_id": "AVI000000042",
    //           "placement_position": "L",
    //           "sponsor_id": 57,
    //           "link": {
    //             "href": "https://www.avicrypto.us/network#"
    //           },
    //           "children": [
    //             {
    //               "transaction": 0,
    //               "name": "Liliana Indriani Agustin",
    //               "relationship": "111",
    //               "package": 1000,
    //               "image": "/static/images/node2.png",
    //               "placement_id": 80,
    //               "id": 81,
    //               "investment": 1000,
    //               "avi_id": "AVI000000043",
    //               "placement_position": "L",
    //               "sponsor_id": 80,
    //               "link": {
    //                 "href": "https://www.avicrypto.us/network#"
    //               },
    //               "children": [
    //                 {
    //                   "transaction": 0,
    //                   "name": "Zulkarnaen last",
    //                   "relationship": "111",
    //                   "package": 1000,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 81,
    //                   "id": 82,
    //                   "avi_id": "AVI000000044",
    //                   "placement_position": "L",
    //                   "sponsor_id": 81,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 1000
    //                 },
    //                 {
    //                   "transaction": 0,
    //                   "name": "Kwan Andreas Kristian",
    //                   "relationship": "111",
    //                   "package": 100,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 81,
    //                   "id": 143,
    //                   "avi_id": "AVI000000099",
    //                   "placement_position": "R",
    //                   "sponsor_id": 81,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 100
    //                 }
    //               ]
    //             },
    //             {
    //               "transaction": 0,
    //               "name": "Ali  Kurniawan",
    //               "relationship": "111",
    //               "package": 1000,
    //               "image": "/static/images/node2.png",
    //               "placement_id": 80,
    //               "id": 84,
    //               "investment": 1000,
    //               "avi_id": "AVI000000046",
    //               "placement_position": "R",
    //               "sponsor_id": 80,
    //               "link": {
    //                 "href": "https://www.avicrypto.us/network#"
    //               },
    //               "children": [
    //                 {
    //                   "transaction": 0,
    //                   "name": " J. Amiruddin  M",
    //                   "relationship": "111",
    //                   "package": 0,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 84,
    //                   "id": 86,
    //                   "avi_id": "AVI000000047",
    //                   "placement_position": "L",
    //                   "sponsor_id": 84,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 0
    //                 },
    //                 {
    //                   "name": "<a href= /add/user?ref=bHBieHV1N2ZFZWV&place=AVI000000001&pos=right&parent_placement_id=AVI000000046>Add New User</a>",
    //                   "relationship": "110"
    //                 }
    //               ]
    //             }
    //           ]
    //         },
    //         {
    //           "transaction": 0,
    //           "name": "SUHERMAN last",
    //           "relationship": "111",
    //           "package": 1000,
    //           "image": "/static/images/node2.png",
    //           "placement_id": 57,
    //           "id": 87,
    //           "investment": 1000,
    //           "avi_id": "AVI000000048",
    //           "placement_position": "R",
    //           "sponsor_id": 57,
    //           "link": {
    //             "href": "https://www.avicrypto.us/network#"
    //           },
    //           "children": [
    //             {
    //               "transaction": 0,
    //               "name": "Lengkap Totok Sukmawanto",
    //               "relationship": "111",
    //               "package": 0,
    //               "image": "/static/images/node2.png",
    //               "placement_id": 87,
    //               "id": 90,
    //               "investment": 0,
    //               "avi_id": "AVI000000051",
    //               "placement_position": "L",
    //               "sponsor_id": 87,
    //               "link": {
    //                 "href": "https://www.avicrypto.us/network#"
    //               },
    //               "children": [
    //                 {
    //                   "transaction": 0,
    //                   "name": "Noppy Iskandar",
    //                   "relationship": "110",
    //                   "package": 1000,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 90,
    //                   "id": 129,
    //                   "avi_id": "AVI000000085",
    //                   "placement_position": "L",
    //                   "sponsor_id": 90,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 1000
    //                 },
    //                 {
    //                   "transaction": 0,
    //                   "name": "Erwin  Susilo",
    //                   "relationship": "110",
    //                   "package": 0,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 90,
    //                   "id": 130,
    //                   "avi_id": "AVI000000086",
    //                   "placement_position": "R",
    //                   "sponsor_id": 90,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 0
    //                 }
    //               ]
    //             },
    //             {
    //               "transaction": 0,
    //               "name": "Shofwan Hadi",
    //               "relationship": "111",
    //               "package": 1000,
    //               "image": "/static/images/node2.png",
    //               "placement_id": 87,
    //               "id": 88,
    //               "investment": 1000,
    //               "avi_id": "AVI000000049",
    //               "placement_position": "R",
    //               "sponsor_id": 87,
    //               "link": {
    //                 "href": "https://www.avicrypto.us/network#"
    //               },
    //               "children": [
    //                 {
    //                   "transaction": 0,
    //                   "name": "Wilda Reflita",
    //                   "relationship": "111",
    //                   "package": 1000,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 88,
    //                   "id": 89,
    //                   "avi_id": "AVI000000050",
    //                   "placement_position": "L",
    //                   "sponsor_id": 87,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 1000
    //                 },
    //                 {
    //                   "transaction": 0,
    //                   "name": "Muhammad Suryanto",
    //                   "relationship": "111",
    //                   "package": 1000,
    //                   "image": "/static/images/node2.png",
    //                   "placement_id": 88,
    //                   "id": 121,
    //                   "avi_id": "AVI000000077",
    //                   "placement_position": "R",
    //                   "sponsor_id": 88,
    //                   "link": {
    //                     "href": "https://www.avicrypto.us/network#"
    //                   },
    //                   "investment": 1000
    //                 }
    //               ]
    //             }
    //           ]
    //         }
    //       ]
    //     },
    //     {
    //       "transaction": 0,
    //       "name": "ASD ASD",
    //       "relationship": "110",
    //       "package": 0,
    //       "image": "/static/images/node2.png",
    //       "placement_id": 1,
    //       "id": 115,
    //       "investment": 0,
    //       "avi_id": "AVI000000071",
    //       "placement_position": "R",
    //       "sponsor_id": null,
    //       "link": {
    //         "href": "https://www.avicrypto.us/network#"
    //       },
    //       "children": [
    //         {
    //           "name": "<a href= /add/user?ref=bHBieHV1N2ZFZWV&place=AVI000000001&pos=left&parent_placement_id=AVI000000071>Add New User</a>",
    //           "relationship": "110"
    //         },
    //         {
    //           "name": "<a href= /add/user?ref=bHBieHV1N2ZFZWV&place=AVI000000001&pos=right&parent_placement_id=AVI000000071>Add New User</a>",
    //           "relationship": "110"
    //         }
    //       ]
    //     }
    //   ]
    // }
    // renderTree(orgData);

    initOrgchart = function(nodeId) {
      var url="";
      if(loaded == true) {
        url = '/network/children/'+nodeId;
      } else {
        url = '/network/init';
        loaded=true;      
      }
      console.log(nodeId)
        $('#chart-container').orgchart({
          'data' : url,
          visibleLevel:4,
          'collapsed': false,
          zoom: false,  
          pan: false,
          toggleSiblingsResp: false,
          nodeTemplate: nodeTemplate,
          'createNode': function($node, data) {
            //console.log($node, data)
            //if ($node.is('.drill-down')) {
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
            // } else if ($node.is('.drill-up')) {
            //   var assoClass = data.className.match(/asso-\w+/)[0];
            //   var drillUpIcon = $('<i>', {
            //     'class': 'fa fa-arrow-circle-up drill-icon',
            //     'click': function() {
            //       $('#chart-container').find('.orgchart:visible').addClass('hidden').end()
            //         .find('.drill-down.' + assoClass).closest('.orgchart').removeClass('hidden');
            //     }
            //   });
            //   $node.append(drillUpIcon);
            // }
          }
        });
      }

      initOrgchart(1)
});
