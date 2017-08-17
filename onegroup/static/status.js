/**
 * Created by Eliot on 8/6/2017.
 */

$(document).ready(function () {
    addInfo();

});

function addInfo()
{
  $.get("/log/status", function (data)
    {
      var LogInfo = data;
      var logStringArrays = new Array;
      for (var i = 0; i<LogInfo["logData"].length; i++)
        {
          var tempvar = LogInfo["logData"][i];
          logStringArrays.push(tempvar);
        }

              var table = $("<table />");
              var infoLength = logStringArrays[0].length;

              var row = $(table[0].insertRow(-1));
              var header = $("<th />");
              header.html("Test");
              row.append(header);

              //Add the data rows.
              for (var i = 1; i < logStringArrays.length; i++) {
                  row = $(table[0].insertRow(-1));
                  for (var j = 0; j < infoLength; j++) {
                      var info = $("<td />");
                      info.html(logStringArrays[i]);
                      row.append(info);
                  }
              }

              var statusTable = $("#statusTable");
              statusTable.html("");
              statusTable.append(table);

    })
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
