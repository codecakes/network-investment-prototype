"use strict";

//Steps:
//1. Implement /network/init/user_id that returns traverse_tree(user) response
//2. On expanding any node, AJAX fires off GET '/network/children/58'
//   Implement this api on the backend return the value of 'children' key like
//{'children': children} and the tree will automagically render the child nodes here

// clicking a node with id=58 automatically calls GET:'/network/children/58'

$(function() {
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
    renderTree = function() {
			console.log("renderTree")
      // TODO: id = getCurrentUserId - implement a function that takes the logged in users user.id
      // then use that here like `/network/init/${id}`
      let oc = $("#chart-container").orgchart({
        data: `/network/init/`,
        nodeId: "id",
        nodeTitle: "name",
        nodeContent: "content",
        ajaxURL: ajaxURL,
        depth: 4,
        zoom: true,
        toggleSiblingsResp: true,
        initCompleted: obj => {
          console.log(`finished rendering network tree`);
          console.log(obj);
        }
      });
    };
  renderTree();
});
