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

              // //Add the data rows for Status.
              // for (var i = 2; i < logStringArrays.length; i++) {
              //     var info = $("<td />");
              //     row = $(table[0].insertRow(-1));
              //     info.html(logStringArrays[i]);
              //     row.append(info);
              //     // for (var j = 0; j < infoLength; j++) {
              //     //     var info = $("<td />");
              //     // }
              // }

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

            //   for (var i = 2; i < logStringArrays.length; i++) {
            //     var routinginfo = $("<td />");
            //     routingrow = $(routingTable[0].insertRow(-1));
            //     routinginfo.html(logStringArrays[i]);
            //     routingrow.append(routinginfo);
            //     // for (var j = 0; j < infoLength; j++) {
            //     //     var info = $("<td />");
            //     // }
            // }

            while(invalid4.test(logStringArrays[counter+1]) == false){
              var routerLength = logStringArrays[counter+1].length;
              routingrow = $(routingTable[0].insertRow(-1));
              for (var k = 0; k < routerLength; k++) {
                var routinginfo = $("<td />");
                routinginfo.html(logStringArrays[counter+1][k]);
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

// // function tableFilter() {
// //   var input, filter, table, tr, td, i;
// //   input = document.getElementById("dateStart");
// //   input2 = document.getElementById("dateEnd");
// //   filter = input.value.toUpperCase();
// //   filter2 = input2.value.toUpperCase();
// //   table = document.getElementById("logTable");
// //   tr = table.getElementsByTagName("tr");
// //   for (i = 0; i < tr.length; i++) {
// //     td = tr[i].getElementsByTagName("td")[0];
// //     co = tr[i].getElementsByTagName("td")[1];
// //     if (td) {
// //       if ((td.innerHTML.toUpperCase().indexOf(filter) > -1) && (co.innerHTML.toUpperCase().indexOf(filter2) > -1)) {
// //         tr[i].style.display = "";
// //       }else {
// //         tr[i].style.display = "none";
// //       }
// //     }
// //   }
// // }
// START HERE LEIO
/**
 * Created by Olive & Eliot on 8/6/2017.
 */

// function addInfo()
// {
// $.get("/log/general", function (data)
//   {
//     var LogInfo = data;
//     var logStringArrays = new Array;
//     var d = new Date();
//     var n = d.getFullYear();
//     for (var i = 0; i<LogInfo["logData"].length; i++)
//       {
//         var tempvar = LogInfo["logData"][i];
//         if(/2017/.test(tempvar)){
//           tempvar = tempvar.split("2017");
//           tempvar[0] = tempvar[0] + n;
//           logStringArrays.push(tempvar);
//       }
//       else{
//         temparray= ["No Date", tempvar];
//         logStringArrays.push(temparray);
//         }
//       }
//             var table = $("<table />");
//             var infoLength = logStringArrays[0].length;

//             var row = $(table[0].insertRow(-1));
//             var header = $("<th />");
//             header.html("TEST");
//             var header2 = $("<th />");
//             header2.html("ICAL");
//             row.append(header);
//             row.append(header2);

//             //Add the data rows.
//             for (var i = 1; i < logStringArrays.length; i++) {
//                 row = $(table[0].insertRow(-1));
//                 for (var j = 0; j < infoLength; j++) {
//                     var info = $("<td />");
//                     info.html(logStringArrays[i][j]);
//                     row.append(info);
//                 }
//             }

//               var statusTable = $("#statusTable");
//               statusTable.html("");
//               statusTable.append(table);

//   })
// }