// /**
//  * Created by Eliot on 8/6/2017.
//  */

$(document).ready(function () {
    addInfo();

});

function addInfo()
{
    var invalid1 = new RegExp("Open VPN CLIENT LIST");
    var invalid2 = new RegExp("Updated");
    var invalid3 = new RegExp("ROUTING TABLE");
    var invalid4 = new RegExp("GLOBAL STATS");
    var invalid5 = new RegExp("Max bcast");
    var invalid6 = new RegExp("END");

  $.get("/log/status", function (data)
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

              var counter = 2;

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

              document.getElementById("currentUsers").innerHTML = counter -3;

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