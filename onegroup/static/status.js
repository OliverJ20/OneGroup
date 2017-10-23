// /**
//  * SERVER STATUS - Created by Eliot on 8/6/2017.
//  */

var logVar = setInterval(addIndexInfo, 1000);
var statVar = setInterval(statusInfo, 1000);
var graphVar = setInterval(createGraph, 1000);
var globalNode = "self";
var byteType = "received"

var graphdataRec = [
  /*TEST DATA
  {User: "Test1", ByteS: 8167},
  {User: "Test2", ByteS: 1492},
  {User: "Test3", ByteS: 2780},
  {User: "Test4", ByteS: 4253},
  {User: "JAMES", ByteS: 2702},
  {User: "Test6", ByteS: 2288},
  {User: "Test7", ByteS: 2022},
  {User: "Test8", ByteS: 6094},
  {User: "Test9", ByteS: 6973},
  {User: "Test10", ByteS: 00153}*/
];

var graphdataSen = [
  /*TEST DATA
  {User: "Mr1", ByteS: 6767},
  {User: "Miss2", ByteS: 4192},
  {User: "f", ByteS: 7280},
  {User: "g", ByteS: 2453},
  {User: "h", ByteS: 7202},
  {User: "j", ByteS: 4388},
  {User: "k", ByteS: 0222},
  {User: "l", ByteS: 2394},
  {User: "t", ByteS: 5173},
  {User: "q", ByteS: 1153}*/
];

$(document).ready(function () {
  addInfo();    
  var today = new Date();
  var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
  var days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  input = document.getElementById("dateStart");
  input.value = days[today.getDay()] + ' ' + months[today.getMonth()];
  document.getElementById('dateStart').placeholder = input.value;
  document.getElementById('dateStart').value = input.value;
  filter = input.value.toUpperCase();
  table = document.getElementById("logTable");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      if ((td.innerHTML.toUpperCase().indexOf(input) > -1)) {
        tr[i].style.display = "";
      }else {
        tr[i].style.display = "none";
      }
    }
  }
});

function statusInfo()
{

  console.log("Status Info: " + globalNode);


  var defAddress;
  if (globalNode === undefined || globalNode == "" || globalNode == null ) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    $.get("/log/status", function(data) {
        console.log(data);
        createStatusTable(data);
    });
  }
  else{
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/connectnode/", 
        data: JSON.stringify({"url" : globalNode + "/log/status", "method" : "GET"}), 
        success: function (data) {
          createStatusTable(data["data"]);
        },
        dataType: "json"
    }); 
  }
}

function createStatusTable(data)
{
    graphdataRec = [];
    graphdataSen = [];
    var LogInfo = data;
    var logStringArrays = new Array;
    var invalid1 = new RegExp("Open VPN CLIENT LIST");
    var invalid2 = new RegExp("Updated");
    var invalid3 = new RegExp("ROUTING TABLE");
    var invalid4 = new RegExp("GLOBAL STATS");
    var invalid5 = new RegExp("Max bcast");
    var invalid6 = new RegExp("END");
    for (var i = 0; i<LogInfo["logData"].length; i++)
      {
        var tempvar = LogInfo["logData"][i];
          if(/invalid1/.test(tempvar) || /invalid2/.test(tempvar) || /invalid3/.test(tempvar) || /invalid4/.test(tempvar) || /invalid5/.test(tempvar) || /invalid6/.test(tempvar)){
               tempvar = LogInfo["logData"].splice(i);
          }
          tempvar = tempvar.split(',');
          logStringArrays.push(tempvar);
      }

      
            var table = $("<table />");
            var routingTable = $("<table />");


            var row = $(table[0].insertRow(-1));
            var nameHeader = $("<th />");
            nameHeader.html("Name");
            var addressHeader = $("<th />");
            addressHeader.html("Address");
            var recHeader = $("<th />");
            recHeader.html("Bytes Received");
            var sentHeader = $("<th />");
            sentHeader.html("Bytes Sent");
            var connectedHeader = $("<th />");
            connectedHeader.html("Connected Since");
            row.append(nameHeader);
            row.append(addressHeader);
            row.append(recHeader);
            row.append(sentHeader);
            row.append(connectedHeader);


            var routingrow = $(routingTable[0].insertRow(-1));
            var nameHeader = $("<th />");
            nameHeader.html("Name");
            var virtualaddressHeader = $("<th />");
            virtualaddressHeader.html("Virtual Address");
            var realaddressHeader = $("<th />");
            realaddressHeader.html("Real Address");
            var lastrefHeader = $("<th />");
            lastrefHeader.html("Last Ref");
            routingrow.append(nameHeader);
            routingrow.append(virtualaddressHeader);
            routingrow.append(realaddressHeader);
            routingrow.append(lastrefHeader);

            var updated = logStringArrays[1];

            var counter = 3;
            
                          while(invalid3.test(logStringArrays[counter]) == false){
                            var tableLength = logStringArrays[counter].length;
                            row = $(table[0].insertRow(-1));
                            console.log(logStringArrays[counter][0]); 
                            console.log(logStringArrays[counter][2]); 
                            graphdataRec.push({"User" : logStringArrays[counter][0],"ByteS" : parseInt(logStringArrays[counter][2])});
                            graphdataSen.push({"User" : logStringArrays[counter][0],"ByteS" : parseInt(logStringArrays[counter][3])});
                            for (var j = 0; j < tableLength; j++) {
                              var info = $("<td />");
                              info.html(logStringArrays[counter][j]);
                              console.log("info: " + info);
                              row.append(info);
                            }
                            counter++;
                          }

                          document.getElementById("currentUsers").innerHTML = counter- 3;

                        while(invalid4.test(logStringArrays[counter+2]) == false){
                          var routerLength = logStringArrays[counter+2].length;
                          routingrow = $(routingTable[0].insertRow(-1));
                          for (var k = 0; k < routerLength; k++) {
                            var routinginfo = $("<td />");
                            routinginfo.html(logStringArrays[counter+2][k]);
                            routingrow.append(routinginfo);
                          }
                          counter++;
            }
            var html = table.html();
            $("#statusTable").html(html);

            /*var statusTable = $("#statusTable");
            statusTable.html("");
            statusTable.append(table);*/

            var statusHtml = routingTable.html();
            $("#statusRouteTable").html(routingTable);
            /*var statusRouteTable = $("#statusRouteTable");
            statusRouteTable.html("");
            statusRouteTable.append(routingTable);*/
}

/**
* LOGPAGE STATUS - Created by Olive & Eliot on 8/6/2017.
*/

function addInfo()
{
  console.log("Log Info: " + globalNode);


  var defAddress;
  if (globalNode === undefined || globalNode ==""||globalNode ==null) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    $.get("/log/general", function(data) {
        console.log(data);
        createLogTable(data);
    });
  }
  else{
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/connectnode/", 
        data: JSON.stringify({"url" : globalNode + "/log/general", "method" : "GET"}), 
        success: function (data) {
          createLogTable(data["data"]);
        },
        dataType: "json"
    }); 
  }
}

function createLogTable(data)
{
  var LogInfo = data;
  var logStringArrays = new Array;
  var d = new Date();
  var n = d.getFullYear();
  var limit = LogInfo["logData"].length;
  
  for (var i = limit; i> 0; i--)
    {
      var tempvar = LogInfo["logData"][i];
      if(/2017/.test(tempvar)){
      tempvar = tempvar.split(n);
      tempvar[0] = tempvar[0] + n;
      logStringArrays.push(tempvar);
    }
    else{
      temparray= ["No Date", tempvar];
      logStringArrays.push(temparray);
    }
    }
          var table = $("<table />");
          var infoLength = logStringArrays[0].length;

          var row = $(table[0].insertRow(-1));
          var header = $("<th />");
          header.html("Date");
          var header2 = $("<th />");
          header2.html("Activity");
          row.append(header);
          row.append(header2);

          //Add the data rows.
          for (var i = 1; i < logStringArrays.length; i++) {
              row = $(table[0].insertRow(-1));
              for (var j = 0; j < infoLength; j++) {
                  var info = $("<td />");
                  info.html(logStringArrays[i][j]);
                  row.append(info);
              }
          }

          var html = table.html();
          $("#logTable").html(html);

         /* var logTable = $("#logTable");
          logTable.html("");
          logTable.append(table);*/
}

function addIndexInfo()
{
  console.log("Log Index Info: " + globalNode);


  var defAddress;
  if (globalNode === undefined|| globalNode == ""||globalNode == null) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    $.get("/log/general", function(data) {
        console.log(data);
        createLogTableShort(data);
    });
  }
  else{
    $.ajax({
        type: "POST",
        contentType: "application/json",
        url: "/connectnode/", 
        data: JSON.stringify({"url" : globalNode + "/log/general", "method" : "GET"}), 
        success: function (data) {
          createLogTableShort(data["data"]);
        },
        dataType: "json"
    }); 
  }
}

function createLogTableShort(data)
{
  var LogInfo = data;
  var logStringArrays = new Array;
  var d = new Date();
  var n = d.getFullYear();
  var limit = LogInfo["logData"].length
  
  for (var i = limit; i> limit - 11; i--)
    {
      var tempvar = LogInfo["logData"][i];
      if(/2017/.test(tempvar)){
      tempvar = tempvar.split(n);
      tempvar[0] = tempvar[0] + n;
      logStringArrays.push(tempvar);
    }
      else{
        temparray= ["No Date", tempvar];
        logStringArrays.push(temparray);
      }
    }
          var table = $("<table />");
          var infoLength = logStringArrays[0].length;

          var row = $(table[0].insertRow(-1));
          var header = $("<th />");
          header.html("Date");
          var header2 = $("<th />");
          header2.html("Activity");
          row.append(header);
          row.append(header2);

          //Add the data rows.
          for (var i = 1; i < logStringArrays.length; i++) {
              row = $(table[0].insertRow(-1));
              for (var j = 0; j < infoLength; j++) {
                  var info = $("<td />");
                  info.html(logStringArrays[i][j]);
                  row.append(info);
              }
          }

          var html = table.html();
          $("#logTableSmall").html(html);
          
          /*var logTableSmall = $("#logTableSmall");
          logTableSmall.html("");
          logTableSmall.append(table);*/
}

function hideButton(){
 document.getElementById('testButton').style.display = "none";
}

function tableFilter() {
    var input, filter, table, tr, td, i;
    input = document.getElementById("dateStart");
    input2 = document.getElementById("dateEnd");
    filter = input.value.toUpperCase();
    filter2 = input2.value.toUpperCase();
    table = document.getElementById("logTable");
    tr = table.getElementsByTagName("tr");
    for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    co = tr[i].getElementsByTagName("td")[1];
    if (td) {
      if ((td.innerHTML.toUpperCase().indexOf(filter) > -1) && (co.innerHTML.toUpperCase().indexOf(filter2) > -1)) {
        tr[i].style.display = "";
      }else {
        tr[i].style.display = "none";
      }
    }
  }
}


// /**
//  * NODE CHANGE and STATUS - Created by Eliot & Oliver on 17/10/2017.
//  */

function nodeChange(){
  console.log(globalNode);
  var newNode = document.getElementById("node");
  var nodeValue = newNode.options[newNode.selectedIndex].value;
  console.log(nodeValue);
  document.getElementById('currentNode').innerHTML = "Node: " + nodeValue;
  globalNode = nodeValue;
  
}

function changeDataType(){
  console.log("Working")
  if(byteType == "received"){
    byteType = "sent";
    document.getElementById('currentActivity').innerHTML = "Bytes Sent";
    return;
  }
  else{
    byteType = "received";
    document.getElementById('currentActivity').innerHTML = "Bytes Received";
    return;
  }
}

function getDataInformation(){
  if(byteType == "received"){
    return graphdataRec;
  }
  else{
    return graphdataSen;
  }
}

function createGraph(){  
  d3.select("#indexSplitRight").selectAll("svg").remove();
  var margin = { top: 40, right: 90, bottom: 30, left: 50 },
    width = 900 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

  var newFormat = d3.format(".0");

  var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], 0.1); 

  var y = d3.scale.linear()
    .range([height, 0], 0.1);

  var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

  var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(newFormat);

  var svg = d3.select("#indexSplitRight").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  var data = getDataInformation();

  x.domain(data.map(function (d) { return d.User; }));
  y.domain([0, d3.max(data, function (d) { return d.ByteS; })]);

  svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

  svg.append("g")
    .attr("class", "y axis")
    .call(yAxis)
    .append("text")
    .attr("transform", "rotate(-90)")

  svg.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "bar")
    .attr("x", function (d) { return x(d.User); })
    .attr("width", x.rangeBand())
    .attr("y", function (d) { return y(d.ByteS); })
    .attr("height", function (d) { return height - y(d.ByteS); })
}


// MISC SCRIPT FUNCTIONS

function hideButton(){
 document.getElementById('testButton').style.display = "none";
}

function displayForm() {
 document.getElementById('formDivleft').style.display = "block";
}

function testDisplay() {
  var e = document.getElementByName("accountType1");
  var strUser = e.options[e.selectedIndex].value;
  console.log(strUser);
  console.log("Usr");
  if(strUser == "Client"){
      document.getElementByName('authType1').style.display = "block";
  }
}

function testfunction()
{
  console.log ("hello there young one");
}

function getIPTablesData()
{
     
     var Input = document.getElementById("INPUT").value;
     var Output = document.getElementById("OUTPUT").value;
      var source = document.getElementById("source").value;
      var port = document.getElementById("port").value;
      var destination = document.getElementById("destination").value;

      var tableData = jQuery("#TABLE option:selected").val();
      var chainData = jQuery("#CHAIN option:selected").val();
      var ifaceData = jQuery("#IFACE option:selected").val();
      var protData = jQuery("#PROT option:selected").val();
      var stateData = jQuery("#STATE option:selected").val();
      var actionData = jQuery("#ACTION option:selected").val();        

      console.log(source);
      console.log(port);
      console.log(destination);
      console.log(tableData);
      console.log(chainData);
      console.log(ifaceData);
      console.log(protData);
      console.log(stateData);
      console.log(actionData);


     // var ipTablesRuleData = {"source": source, "port": port, "destination":destination, "tableData": tableData, "chainData": chainData, "ifaceData": ifaceData, "protData":protData, "stateData": stateData, "actionData":actionData};




      
}


function checkForm() {
// Currently not working
  document.getElementById('submitDiv').style.display = "block";
  var email1 = document.forms["userForm"]["email1"].value;
  var pass1 = document.forms["userForm"]["pass1"].value;
  var atpos = email1.indexOf("@");
  var dotpos = email1.lastIndexOf(".");
  if (atpos<1 || dotpos<atpos+2 || dotpos+2 >= email1.length) {
      alert("Not a valid e-mail address");
      document.getElementById('submitDiv').style.display = "block";
      return false;
  }
  else {
    document.getElementById('submitDiv').style.display = "block";
    return true;
  }
}

function enableServer() {
  x = document.getElementById("status");
  if(statusColour==1) {
    x.style.color = 'red';
    statusColour = 2;
  }
  else if(status!=1) {
    x.style.color = 'green';
    statusColour = 1;
  }
}
