/**
 * Created by Oliver on 8/6/2017.
 */

$(document).ready(function () {
    addInfo();

});

function addInfo()
{
  $.get("/req", function (data)
    {
      var LogInfo = data;
      var logStringArrays = new Array
      for (var i = 0; i<LogInfo["logData"].length; i++)
        {
          var tempvar = LogInfo["logData"][i].split(" ");
          logStringArrays.push(tempvar);
        }
              var table = $("<table />");
              var infoLength = logStringArrays[0].length;

              var row = $(table[0].insertRow(-1));
              var header = $("<th />");
              header.html("User");
              var header2 = $("<th />");
              header2.html("Activity");
              var header3 = $("<th />");
              header2.html("Approve?");
              row.append(header);
              row.append(header2);
              row.append(header3);

              //Add the data rows.
              for (var i = 1; i < logStringArrays.length; i++) {
                  row = $(table[0].insertRow(-1));
                  for (var j = 0; j < infoLength; j++) {
                      var info = $("<td />");
                      info.html(logStringArrays[i][j]);
                      row.append(info);
                  }
                  var apprButton = document.createElement("button");
                  apprButton.innerHTML = "Approve";
                  apprButton.setAttribute("id","user-app-"+logStringArrays[i]);
                  row.append(apprButton);
                  var decButton = document.createElement("button");
                  decButton.innerHTML = "Decline";
                  decButton.setAttribute("id","user-dec-"+logStringArrays[i]);
                  row.append(decButton);
              }

              var userReqTable = $("#userReqTable");
              userReqTable.html("");
              userReqTable.append(table);

    })
}
//OJ ORIGINAL
// function addInfo()
// {
//   $.get("/logtestdata/", function (data)
//     {
//
//
//        var LogInfo = data;
//       // var logStringArray = ["friday 12:00pm server hacked","monday 12:00pm server hacked", "thursday 2:00pm server hacked", "sunday 1:00pm nerd" ];
//
//
//
//         var main = $('<div class = "tableScroll">');
//         var table = $('<table>');
//         var header = $('<tr>');
//         //header.append($('<th style="width:auto;white-space:nowrap;">'));
//         header.append($('<th style="width:auto;white-space:nowrap;">').html("Log report "));
//         table.append(header);
//         console.log(LogInfo);
//         console.log(LogInfo["logData"][0]);
//         console.log(LogInfo["logData"].length);
//         for (var i = 0; i<LogInfo["logData"].length; i++)
//         {
//             var row = $('<tr>');
//             row.append($('<td style="width:auto;white-space:nowrap;text-align:right;" ">').html(LogInfo["logData"][i]));
//             console.log(LogInfo["logData"][i])
//             //var cell = $('<td style="width:auto;white-space:nowrap;text-align:center;" >');
//            // cell.html("hello");
//            // row.append(cell);
//             table.append(row);
//
//         }
//
//         main.append(table);
//         var mainhtml = main.html();
//         $('#logTable').html(mainhtml);
//
//       // var logInfo = $('<p>').html(logInfo[0]);
//       // div.append(div);
//       // div.append(logInfo);
//       // $('#FrontLogInfo').html(div.html());
//
//     })
// }

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
