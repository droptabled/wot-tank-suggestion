var width = window.innerWidth;
var height = window.innerHeight-50;
var tank_width = 160;
var tank_height = 100;
var svg = d3.select("svg").attr("width", width).attr("height", height);
var g = d3.select("#gcontainer")

var force = d3.forceSimulation() 
  .force("link", d3.forceLink().id(function(d) { return d.index }).distance(20));
  //.force("center", ;

function dragstarted(d) {
  tank_select = $(event.target).parents(".select-btn")
  if(tank_select.length == 0){
    if (!d3.event.active) force.alphaTarget(0.5).restart();
    d.fx = d.x;
  }
  // if a parent of type select-btn is found, treat as a button click
  else{
    $.ajax({
      url: 'improve_tank',
      data: {
        tank: tank_select.parents("g.node")[0].__data__.id,
        improvement: tank_select.data("option")
      },
      dataType: 'json',
      success: function (json) {
      }
    });
  }
}

function dragged(d) {
  d.fx = d3.event.x;
}

function dragended(d) {
  if (!d3.event.active) force.alphaTarget(0.5);
  d.fx = null;
}

function generate_buttons(obj) {
  var gselect = obj.append('g').attr('class', 'selection');
  var rectborder = 3
  var font_size = 16
  var img_size = tank_width/2 - rectborder*2;
  var improvements = ['kills', 'damage', 'durability', 'survival', 'shots hit', 'spotting']; 
  for(var i=0;i<6;i++) {
    var gbtn = gselect.append('g').attr('class', 'select-btn').attr('data-option', improvements[i]);
    gbtn.append('rect')
      .attr('id', improvements[i])
      .attr('class', 'improvement-box')
      .attr('width', tank_width/2)
      .attr('height', tank_height)
      .attr('x', -tank_width + i*tank_width/2)
      .attr('y', tank_height);
    gbtn.append('image')
      .attr('width', img_size)
      .attr('height', img_size)
      .attr('x', -tank_width + i*tank_width/2 + rectborder)
      .attr('y', tank_height + (tank_height - img_size))
      .attr('href', '/static/explorerbuttons/' + improvements[i] + '.png');
    var select_text = gbtn.append('text')
      .attr('x', -tank_width + i*tank_width/2)
      .attr('y', tank_height + font_size)
      .attr('font-size', font_size);
    select_text.append('tspan')
      .attr('x', -tank_width + i*tank_width/2 + tank_width/2/2)
      .attr('text-anchor', 'middle')
      .text('More')
    select_text.append('tspan')
      .attr('x', -tank_width + i*tank_width/2 + tank_width/2/2)
      .attr('dy', '1em')
      .attr('text-anchor', 'middle')
      .text(improvements[i])
  }
}

$("#start").click(function () {
  $.ajax({
    url: 'root_tank',
    data: { tank: $("#tank").val() },
    dataType: 'json',
    success: function (json) {
      var link = g.selectAll(".link").data(json.links).enter().append("line")
        .attr("stroke-width", "3")
        .attr("stroke", "black");
      
      var node = g.selectAll(".node")
        .data(json.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended)
        );

      // draw root node picture and name
      node.append('rect')
        .attr('width', tank_width)
        .attr('height', tank_height)
        .attr('fill', function (d) { return "url('#" + d.nation + "')"; });
      node.append("text")
          .attr("dx", function (d) { return tank_width/2 - d.name.length*5; })
          .attr("dy", tank_height/2)
          .style("font-size", "15px")
          .text(function (d) { return d.name });
      
      generate_buttons(node);

      force.nodes(json.nodes).force("link").links(json.links);
      //initialize root node at center of page
      json.nodes[0].x = width/2;
      force.on("tick", function () {
        //link.attr("x1", function (d) { return d.source.x; })
        // .attr("y1", function (d) { return d.source.y; })
        // .attr("x2", function (d) { return d.target.x; })
        // .attr("y2", function (d) { return d.target.y; });
       node.attr("transform", function (d) {
         return "translate(" + d.x + "," + d.y + ")";
       });
      });
    }
  });
});
