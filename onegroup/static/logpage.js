/**
 * Created by Olive & Eliot on 8/6/2017.
 */

$(document).ready(function () {
    console.log ("hello there young one");
    addInfo();
    var today = new Date();
    var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
    var days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    input = days[today.getDay()] + ' ' + months[today.getMonth()];
    document.getElementById('dateStart').placeholder = input;
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

function convertDate(){
  
}

function addInfo()
{
  $.get("/log/general", function (data)
    {
      console.log ("Begin");
      var LogInfo = data;
      var logStringArrays = new Array;
      var d = new Date();
      var n = d.getFullYear();
      for (var i = 0; i<LogInfo["logData"].length; i++)
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
