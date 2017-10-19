// /**
//  * SERVER STATUS - Created by Eliot on 8/6/2017.
//  */

var logVar = setInterval(addIndexInfo(), 1000);
var statVar = setInterval(statusInfo(), 1000);
var globalNode = "self";

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
  console.log("Status Info");
  var invalid1 = new RegExp("Open VPN CLIENT LIST");
  var invalid2 = new RegExp("Updated");
  var invalid3 = new RegExp("ROUTING TABLE");
  var invalid4 = new RegExp("GLOBAL STATS");
  var invalid5 = new RegExp("Max bcast");
  var invalid6 = new RegExp("END");

  var defAddress;
  if (globalNode === undefined) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    defAddress = "/log/status";
  }
  else{
    defAddress = "http://" + globalNode + "/log/status";
  }
  
$.get(defAddress, function (data)
  {
    var LogInfo = data;
    var logStringArrays = new Array;
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
                            for (var j = 0; j < tableLength; j++) {
                              var info = $("<td />");
                              info.html(logStringArrays[counter][j]);
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
            var statusTable = $("#statusTable");
            statusTable.html("");
            statusTable.append(table);

            var statusRouteTable = $("#statusRouteTable");
            statusRouteTable.html("");
            statusRouteTable.append(routingTable);

  })
}

/**
* LOGPAGE STATUS - Created by Olive & Eliot on 8/6/2017.
*/

function addInfo()
{
  var defAddress;
  if (globalNode === undefined) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    defAddress = "/log/general";
  }
  else{
    defAddress = "http://" + globalNode + "/log/general";
  }
  
  console.log(defAddress);
  console.log(defAddress.value);
  console.log(defAddress.toString);

  $.get(defAddress, function (data)
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

              var logTable = $("#logTable");
              logTable.html("");
              logTable.append(table);

    })
}

function addIndexInfo()
{
  console.log("Index Info");
  var defAddress;
  if (globalNode === undefined) {
    defAddress = "self";
  }
  if (globalNode == "self"){
    defAddress = "/log/general";
  }
  else{
    defAddress = "http://" + globalNode + "/log/general";
  }
  
  $.get(defAddress, function (data)
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

              var logTableSmall = $("#logTableSmall");
              logTableSmall.html("");
              logTableSmall.append(table);
  })
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